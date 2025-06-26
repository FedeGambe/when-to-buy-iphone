from datetime import datetime, timedelta
import pandas as pd

def df_espanso(df):
    expanded_rows = []
    # Per ogni riga del file, genera tutte le date tra start e end
    for _, row in df.iterrows():
        start_date = datetime.strptime(row['day_start'].strip(), "%d-%m-%Y")
        end_date = datetime.strptime(row['day_end'].strip(), "%d-%m-%Y")
        price = float(row['price'])

        # Genera ogni data nel range
        current_date = start_date
        while current_date <= end_date: #quando la data corrente è minore o uguale alla data finale 
            #Continua a ciclare finché la data corrente non supera la data finale (end_date). In pratica, itera giorno per giorno.
            expanded_rows.append({ # espande le righe con per ogni giorno tra start e end
                "Data": current_date.strftime("%d-%m-%Y"),
                "Prezzo": price
            })
            current_date += timedelta(days=1) #Passa al giorno successivo, aggiungendo un giorno alla data corrente.
    return expanded_rows

def assegna_quadrimestre(df):
    df['Trimestre'] = pd.cut(
        df['Giorni_dal_lancio'],
        bins=[-1, 90, 180, 270, 365, 455, 545, 635, 730],
        labels=['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'],
        include_lowest=True
    )
    return df

def processa_df(df, label):
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
    #df = df[df['Data'] <= df['Data'].min() + pd.DateOffset(years=1)].copy()
    df['Giorni_dal_lancio'] = (df['Data'] - df['Data'].min()).dt.days
    df = assegna_quadrimestre(df)
    df['Modello'] = label
    return df


def trimestri_stats(df, label):
    grouped = df.dropna(subset=['Trimestre']).groupby('Trimestre', observed=True)['Prezzo'].agg(['mean', 'min', 'max', 'std']).reset_index()
    grouped['Modello'] = label
    return grouped

def prezzo_trimestri_stats(df):
    cambio_prezzo = df['Prezzo'].iloc[-1] - df['Prezzo'].iloc[0]
    max_calo = df['Prezzo'].max() - df['Prezzo'].min()
    volatilita = df['Prezzo'].std()

    return pd.Series({
        'Prezzo Iniziale': df['Prezzo'].iloc[0],
        'Prezzo Finale': df['Prezzo'].iloc[-1],
        'Prezzo Medio Trimestre': round(df['Prezzo'].mean(),2),
        'Variazione Totale (€)': round(cambio_prezzo,2),
        'Variazione Totale (%)': round((cambio_prezzo / df['Prezzo'].iloc[0]) * 100 if df['Prezzo'].iloc[0] != 0 else None,2),
        'Oscillazione Massima (€)': max_calo,
        'Volatilità (std dev)': volatilita
    })