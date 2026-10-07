"""Grafici plotly per il notebook di confronto. Ogni funzione restituisce una Figure."""
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import calcoli

# colori della cover (caldo, freddo) + pastelli della skill crea-pagina-html
PALETTE = {'iPhone14': '#e8593c', 'iPhone15': '#8fc3e0', 'iPhone16': '#a6d96a', 'iPhone17': '#c9a8e8'}
TRIMESTRI = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']
GIORNI_TRIMESTRE = {'T1': (0, 90), 'T2': (91, 180), 'T3': (181, 270), 'T4': (271, 365),
                    'T5': (366, 455), 'T6': (456, 545), 'T7': (546, 635), 'T8': (636, 730)}
COLORI_TRIMESTRE = ['#CCCCCC', '#90EE90', '#FFD580', '#DA70D6', '#87CEEB', '#F08080', '#F0E68C', '#B0A0FF']
MESI = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
TEMPLATE = 'plotly_dark'


def _colore(nome):
    return PALETTE.get(nome, '#BBBBBB')


def sconto_per_giorno(dati, orizzonte=730):
    fig = go.Figure()
    for (t, (a, b)), col in zip(GIORNI_TRIMESTRE.items(), COLORI_TRIMESTRE):
        fig.add_vrect(x0=a, x1=b, fillcolor=col, opacity=0.12, layer='below', line_width=0,
                      annotation_text=t, annotation_position='top left')
    for m, df in dati.items():
        f = df[df['Giorni_dal_lancio'] <= orizzonte]
        fig.add_trace(go.Scatter(x=f['Giorni_dal_lancio'], y=f['Sconto'] * 100, name=m, mode='lines',
                                 line=dict(color=_colore(m), width=2),
                                 customdata=f[['Data', 'Prezzo']],
                                 hovertemplate='%{customdata[0]|%d/%m/%Y} - %{y:.1f}% (%{customdata[1]:.0f} €)<extra>' + m + '</extra>'))
    fig.add_hline(y=0, line_dash='dot', line_color='gray')
    fig.update_layout(title='Sconto rispetto al prezzo di lancio', xaxis_title='Giorni dal lancio',
                      yaxis_title='Variazione prezzo (%)', template=TEMPLATE, height=550)
    return fig


def heatmap_trimestri(dati):
    z = pd.DataFrame({m: -df.groupby('Trimestre', observed=True)['Sconto'].mean() * 100 for m, df in dati.items()}).T
    z = z.reindex(columns=TRIMESTRI)
    fig = px.imshow(z, text_auto='.1f', color_continuous_scale='YlGnBu', aspect='auto',
                    labels=dict(x='Trimestre', y='Modello', color='Sconto medio %'),
                    title='Sconto medio sul prezzo di lancio per trimestre (%)')
    return fig.update_layout(template=TEMPLATE, height=350)


def box_trimestri(dati):
    df = pd.concat(dati.values())
    df = df[df['Trimestre'].isin(TRIMESTRI[:4])].assign(Sconto_pct=lambda d: -d['Sconto'] * 100)
    fig = px.box(df, x='Trimestre', y='Sconto_pct', color='Modello', color_discrete_map=PALETTE,
                 category_orders={'Trimestre': TRIMESTRI}, labels={'Sconto_pct': 'Sconto (%)'},
                 title='Distribuzione dello sconto giornaliero per trimestre (primo anno)')
    return fig.update_layout(template=TEMPLATE, height=500)


def minimi(riepilogo):
    fig = go.Figure(go.Bar(x=riepilogo['Modello'], y=riepilogo['Risparmio %'],
                           marker_color=[_colore(m) for m in riepilogo['Modello']],
                           text=[f"{p:.0f} €<br>{d}<br>giorno {g}" for p, d, g in
                                 zip(riepilogo['Prezzo minimo'], riepilogo['Data minimo'], riepilogo['Giorno dal lancio'])],
                           textposition='outside'))
    fig.update_layout(title='Prezzo minimo del primo anno: risparmio sul lancio', yaxis_title='Risparmio (%)',
                      yaxis_range=[0, riepilogo['Risparmio %'].max() * 1.35], template=TEMPLATE, height=450)
    return fig


def costo_attesa(curve):
    """curve = {modello: DataFrame di analisi.costo_attesa}"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=(
        "Spreco: € sopra il prezzo minimo dell'anno se compri al giorno N",
        "Guadagno dell'attesa: € risparmiabili aspettando il minimo successivo"))
    for m, c in curve.items():
        for riga, col in ((1, 'spreco'), (2, 'guadagno_attesa')):
            fig.add_trace(go.Scatter(x=c.index, y=c[col], name=m, legendgroup=m, showlegend=riga == 1,
                                     line=dict(color=_colore(m))), row=riga, col=1)
    fig.update_xaxes(title_text='Giorni dal lancio', row=2, col=1)
    fig.update_yaxes(title_text='€', row=1, col=1)
    fig.update_yaxes(title_text='€', row=2, col=1)
    return fig.update_layout(template=TEMPLATE, height=650)


def stagionalita(mensile, settimanale):
    """mensile/settimanale: {anno di vita: dati} da calcoli.stagionalita_*. Bottoni (vedi POST_BOTTONI): anno di vita per
    entrambi i grafici, 'Tutti'/modello per quello settimanale."""
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.22, row_heights=[0.4, 0.6], subplot_titles=(
        'Variazione % media del prezzo per mese (da settembre)', 'Variazione % media per settimana (da settembre)'))
    ordine_mesi = [MESI[m - 1] for m in calcoli.ORDINE_MESI]
    for i, (n, m) in enumerate(mensile.items()):
        fig.add_trace(go.Heatmap(z=m.values, x=ordine_mesi, y=list(m.index), colorscale='RdYlGn_r', zmid=0, meta=dict(anno=i),
                                 visible=i == 0, colorbar=dict(title='%', len=0.35, y=0.85), hoverongaps=False,
                                 hovertemplate='%{y} %{x}: %{z:.1f}%<extra></extra>'), row=1, col=1)
        for j, (nome, s) in enumerate(settimanale[n].iterrows()):
            fig.add_trace(go.Bar(x=list(range(len(s))), y=s.values, showlegend=False, visible=i == 0 and j == 0, customdata=s.index,
                                 meta=dict(anno=i, mod=j), hovertemplate='settimana %{customdata}: %{y:.1f}%<extra></extra>',
                                 marker_color=['#4CD97B' if v < 0 else '#FF4C4C' for v in s.values]), row=2, col=1)
    fig.update_layout(meta=dict(anni=[f'Anno {n}' for n in mensile], modelli=list(settimanale[1].index)))
    pos = {w: i for i, w in enumerate(calcoli.ORDINE_SETTIMANE)}
    for sett, nome in ((28, 'Prime Day'), (47, 'Black Friday'), (52, 'Natale')):
        fig.add_vline(x=pos[sett], line_dash='dot', line_color='gray', annotation_text=nome, row=2, col=1)
    # un tick per mese, sulla prima settimana del mese (giovedi' della settimana ISO, come nel resto dell'analisi)
    mese = [date.fromisocalendar(2026, w, 4).month for w in calcoli.ORDINE_SETTIMANE]
    tick = [i for i, m in enumerate(mese) if i == 0 or m != mese[i - 1]]
    fig.update_xaxes(title_text='Mese', title_standoff=22, tickvals=tick, ticktext=[MESI[mese[i] - 1] for i in tick], row=2, col=1)
    return fig.update_layout(template=TEMPLATE, height=750, margin=dict(b=110))


def offerte(profilo):
    colonne = list(profilo.columns)
    fig = make_subplots(rows=1, cols=len(colonne), subplot_titles=colonne)
    for i, c in enumerate(colonne, 1):
        fig.add_trace(go.Bar(x=profilo.index, y=profilo[c], marker_color=[_colore(m) for m in profilo.index],
                             showlegend=False), row=1, col=i)
    return fig.update_layout(title='Profilo delle offerte', template=TEMPLATE, height=400)


def effetto_lancio(finestre):
    fig = go.Figure()
    for nome, serie in finestre.items():
        fig.add_trace(go.Scatter(x=serie.index, y=serie.values, name=nome, mode='lines',
                                 line=dict(color=_colore(nome.split(' ')[0]), width=2)))
    fig.add_vline(x=0, line_dash='dot', line_color='gray', annotation_text='lancio nuovo modello')
    fig.update_layout(title='Prezzo del modello precedente intorno al lancio del successivo',
                      xaxis_title='Giorni dal lancio del nuovo modello', yaxis_title='Variazione dal primo giorno (%)',
                      template=TEMPLATE, height=500)
    return fig


CONFIG_HTML = dict(displaylogo=False, responsive=True, displayModeBar='hover',
                   modeBarButtonsToRemove=['select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'])


# bottoni tondi (classe .gruppo della pagina) sopra il grafico: uno per etichetta in layout.meta, mostrano le tracce 2i e 2i+1
POST_BOTTONI = """
var gd = document.getElementById('{plot_id}'), sel = [0, 0], gruppi = [];
function mostra() {
  gruppi.forEach(function (g, k) { g.querySelectorAll('button').forEach(function (b, i) { b.className = i === sel[k] ? 'on' : ''; }); });
  Plotly.restyle(gd, {visible: gd.data.map(function (t) {
    return t.meta.anno === sel[0] && (t.meta.mod === undefined || t.meta.mod === sel[1]); })});
}
function gruppo(etichetta, nomi, k, tra) {
  var g = document.createElement('div'), e = document.createElement('span');
  g.className = 'gruppo'; g.style.marginBottom = '8px'; e.className = 'et'; e.textContent = etichetta; g.appendChild(e);
  nomi.forEach(function (nome, i) {
    var b = document.createElement('button'); b.textContent = nome; b.onclick = function () { sel[k] = i; mostra(); };
    g.appendChild(b);
  });
  gruppi.push(g);
  if (!tra || gd.clientWidth < 700) {  // schermi stretti: i bottoni vanno a capo, restano sopra il grafico
    gd.parentNode.insertBefore(g, gd); return; }
  // tra i due grafici: sopra il titolo del secondo, allineato al suo asse
  gd.parentNode.style.position = 'relative'; g.style.position = 'absolute'; g.style.zIndex = 5; g.style.margin = 0;
  gd.parentNode.appendChild(g);
  function posiziona() {
    var f = gd._fullLayout; if (!f) return;
    g.style.left = f._size.l + 'px'; g.style.top = (f._size.t + (1 - f.yaxis2.domain[1]) * f._size.h - 36) + 'px';
  }
  gd.on('plotly_afterplot', posiziona); posiziona();
}
gruppo('Anno di vita', gd.layout.meta.anni, 0);
gruppo('Grafico settimanale', gd.layout.meta.modelli, 1, true);
mostra();
"""


def stile_html(fig):
    """Layout unico per la pagina docs/index.html (skill crea-pagina-html): sfondo trasparente, testo chiaro, legenda sotto."""
    testo = '#d9ccaf'
    fig.update_layout(template='none', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='ui-monospace, Consolas, monospace', size=11, color=testo),
                      legend=dict(orientation='h', y=-.18), hovermode='x unified' if all(t.type == 'scatter' for t in fig.data) else 'closest',
                      hoverlabel=dict(bgcolor='#0a1018', bordercolor='#d9ccaf', font=dict(color='#efe3c8')),
                      modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0)', color=testo, activecolor='#efe3c8'))
    fig.update_xaxes(gridcolor='rgba(255,255,255,.1)', zeroline=False, linecolor='rgba(255,255,255,.2)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,.1)', zeroline=False, linecolor='rgba(255,255,255,.2)')
    fig.update_traces(selector=dict(type='scatter'), line_width=2.4)
    return fig
