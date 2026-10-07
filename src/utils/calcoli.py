"""Analisi "quando comprare". Ogni funzione prende `dati` = {nome_modello: DataFrame di carica_modello}."""
import pandas as pd

GIORNI_CHIAVE = (30, 90, 180, 365)


def tabella_sconti(dati, giorni=GIORNI_CHIAVE):
    """Sconto vs prezzo di lancio nei primi N giorni: medio, massimo e % di giorni sotto il prezzo di lancio."""
    righe = []
    for m, df in dati.items():
        for n in giorni:
            f = df[df['Giorni_dal_lancio'] <= n]
            righe.append({'Modello': m, 'Giorni': n,
                          'Sconto medio %': 0.0 - f['Sconto'].mean() * 100,  # 0.0 - x evita "-0.0"
                          'Sconto massimo %': 0.0 - f['Sconto'].min() * 100,
                          '% giorni sotto lancio': (f['Sconto'] < 0).mean() * 100})
    return pd.DataFrame(righe).round(2)


def riepilogo_minimi(dati, orizzonte=365):
    """Giorno e prezzo migliori entro `orizzonte` giorni dal lancio."""
    righe = []
    for m, df in dati.items():
        f = df[df['Giorni_dal_lancio'] <= orizzonte]
        i = f['Prezzo'].idxmin()  # primo giorno al prezzo minimo
        righe.append({'Modello': m, 'Prezzo lancio': f['Prezzo'].iloc[0], 'Prezzo minimo': f.loc[i, 'Prezzo'],
                      'Data minimo': f.loc[i, 'Data'].date(), 'Giorno dal lancio': f.loc[i, 'Giorni_dal_lancio'],
                      'Risparmio €': f['Prezzo'].iloc[0] - f.loc[i, 'Prezzo'],
                      'Risparmio %': -f.loc[i, 'Sconto'] * 100})
    return pd.DataFrame(righe).round(2)


def costo_attesa(df, orizzonte=365):
    """Per ogni giorno N dal lancio:
    - spreco: € pagati sopra il minimo dell'anno (comprare a N invece che nel giorno migliore)
    - guadagno_attesa: € risparmiabili aspettando il minimo da N in poi (con il senno di poi)."""
    p = df[df['Giorni_dal_lancio'] <= orizzonte].set_index('Giorni_dal_lancio')['Prezzo']
    minimo_futuro = p.iloc[::-1].cummin().iloc[::-1]
    return pd.DataFrame({'spreco': p - p.min(), 'guadagno_attesa': p - minimo_futuro})


def _offerte_modello(df, finestra, soglia):
    p = df.set_index('Data')['Prezzo'].asfreq('D')  # i giorni senza dato restano NaN
    base = p.rolling(finestra, min_periods=finestra // 2).median()
    sotto = p < base * (1 - soglia)
    gruppo = (sotto != sotto.shift()).cumsum()[sotto]
    runs = [(p[g.index], base[g.index]) for _, g in gruppo.groupby(gruppo)]
    mesi = p.notna().sum() / 30.44
    return {'Variazioni / mese': (p.dropna().diff().fillna(0) != 0).sum() / mesi,
            'Offerte / anno': len(runs) / mesi * 12,
            'Durata media offerta (gg)': sum(len(r) for r, _ in runs) / len(runs) if runs else 0,
            'Sconto medio offerta %': 100 * sum(1 - (r / b).mean() for r, b in runs) / len(runs) if runs else 0}


def profilo_offerte(dati, finestra=60, soglia=0.03):
    """Offerta = periodo continuo in cui il prezzo e' almeno `soglia` sotto la mediana mobile degli ultimi `finestra` giorni."""
    return pd.DataFrame({m: _offerte_modello(df, finestra, soglia) for m, df in dati.items()}).T.round(2)


def variazioni_periodo(dati, freq):
    """% di variazione del prezzo per periodo ('MS' mensile, 'W' settimanale), una colonna per modello.
    Il primo periodo e' misurato dal prezzo di lancio; quelli dopo un buco nei dati restano NaN."""
    def var(df):
        ultimo = df.set_index('Data')['Prezzo'].resample(freq).last()
        prima = ultimo.shift(1)
        prima.iloc[0] = df['Prezzo'].iloc[0]  # solo il primo periodo parte dal lancio, i buchi restano NaN
        return (ultimo / prima - 1) * 100
    return pd.DataFrame({m: var(df) for m, df in dati.items()})


ORDINE_MESI = list(range(9, 13)) + list(range(1, 9))  # l'anno di un iPhone parte a settembre
ORDINE_SETTIMANE = list(range(36, 54)) + list(range(1, 36))


def _orizzonti(dati):
    """Orizzonti in anni (1, 2, ...) fino alla storia piu' lunga."""
    return range(1, int(max((df['Data'].max() - df['Data'].min()).days for df in dati.values()) // 365) + 2)


def _per_orizzonte(dati, freq, chiave, ordine):
    """{anno di vita: variazione % media per `chiave` (mese/settimana), colonne in `ordine`, riga = modello};
    la chiave N e' l'N-esimo anno di vita del modello (dal lancio): se non e' ancora arrivato a quell'anno la cella resta vuota."""
    v = variazioni_periodo(dati, freq)
    if freq == 'MS':  # mesi dal mese di lancio: l'anno 1 va da settembre ad agosto per tutti i modelli
        anno = pd.DataFrame({m: ((v.index.year - df['Data'].min().year) * 12 + v.index.month - df['Data'].min().month) // 12 + 1
                             for m, df in dati.items()}, index=v.index)
    else:
        anno = pd.DataFrame({m: (v.index - df['Data'].min()).days // 365 + 1 for m, df in dati.items()}, index=v.index)
    out = {}
    for n in _orizzonti(dati):
        x = v.where(anno == n)
        out[n] = x.groupby(chiave(x.index)).mean().T.reindex(columns=ordine)
    return out


def stagionalita_mensile(dati):
    """{anno di vita: variazione % media per mese, righe = modello, colonne = mesi da settembre ad agosto}."""
    return _per_orizzonte(dati, 'MS', lambda i: i.month, ORDINE_MESI)


def stagionalita_settimanale(dati):
    """{anno di vita: variazione % media per settimana ISO da 36 a 35; righe = 'Tutti' (media sui modelli) e un modello ciascuno}."""
    return {n: pd.concat([t.mean().rename('Tutti').to_frame().T, t.iloc[::-1]])
            for n, t in _per_orizzonte(dati, 'W', lambda i: i.isocalendar().week.values, ORDINE_SETTIMANE).items()}


def effetto_lancio(dati, giorni=28):
    """Per ogni coppia di modelli consecutivi (vecchio, nuovo): andamento % del prezzo del vecchio nei +-`giorni`
    giorni intorno al lancio del nuovo (primo giorno dei suoi dati), rispetto al primo prezzo disponibile."""
    nomi = list(dati)
    out = {}
    for vecchio, nuovo in zip(nomi, nomi[1:]):
        lancio = dati[nuovo]['Data'].min()
        p = dati[vecchio].set_index('Data')['Prezzo'].asfreq('D')
        w = p.loc[lancio - pd.Timedelta(days=giorni): lancio + pd.Timedelta(days=giorni)]
        w.index = (w.index - lancio).days
        out[f"{vecchio} (lancio {nuovo})"] = (w / w.dropna().iloc[0] - 1) * 100
    return pd.DataFrame(out)


def raccomandazione(dati, orizzonte=365):
    """Testo riassuntivo: quando e' stato storicamente il momento migliore."""
    r = riepilogo_minimi(dati, orizzonte)
    righe = [f"{x['Modello']}: minimo {x['Prezzo minimo']:.0f} € il {x['Data minimo']} (giorno {x['Giorno dal lancio']}), "
             f"-{x['Risparmio %']:.1f}% sul lancio" for _, x in r.iterrows()]
    medie = pd.DataFrame({m: df[df['Giorni_dal_lancio'] <= orizzonte].groupby('Trimestre', observed=True)['Sconto'].mean()
                          for m, df in dati.items()})
    righe.append("Trimestre con sconto medio più alto: " + ", ".join(f"{m} {t}" for m, t in medie.idxmin().items()))
    righe.append(f"Giorno mediano del prezzo minimo: {r['Giorno dal lancio'].median():.0f} dal lancio; "
                 f"risparmio medio al minimo: {r['Risparmio %'].mean():.1f}%")
    return '\n'.join(righe)
