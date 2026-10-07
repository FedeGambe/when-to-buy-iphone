"""Grafici plotly per il notebook di confronto. Ogni funzione restituisce una Figure."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.18, row_heights=[0.4, 0.6], subplot_titles=(
        'Variazione % media del prezzo per mese', 'Variazione % media per settimana (media sui modelli)'))
    fig.add_trace(go.Heatmap(z=mensile.values, x=MESI, y=list(mensile.index), colorscale='RdYlGn_r', zmid=0,
                             colorbar=dict(title='%', len=0.35, y=0.85),
                             hovertemplate='%{y} %{x}: %{z:.1f}%<extra></extra>'), row=1, col=1)
    fig.add_trace(go.Bar(x=settimanale.index, y=settimanale.values, showlegend=False,
                         marker_color=['#4CD97B' if v < 0 else '#FF4C4C' for v in settimanale.values]), row=2, col=1)
    for sett, nome in ((28, 'Prime Day'), (47, 'Black Friday'), (52, 'Natale')):
        fig.add_vline(x=sett, line_dash='dot', line_color='gray', annotation_text=nome, row=2, col=1)
    fig.update_xaxes(title_text='Settimana ISO', row=2, col=1)
    return fig.update_layout(template=TEMPLATE, height=750)


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
