import pandas as pd
import plotly.express as px

# Carica i dati
d1 = pd.read_csv("Dataset/iPhone15.csv")
d2 = pd.read_csv("Dataset/iPhone16.csv")
d3 = pd.read_csv("Dataset/iPhone15.csv")

# Converti le date
d1['Data'] = pd.to_datetime(d1['Data']) 
d3['Data'] = pd.to_datetime(d1['Data']) + pd.DateOffset(years=1)  # Trasla di un anno
d2['Data'] = pd.to_datetime(d2['Data'])

# Aggiungi una colonna per distinguere i dataset
d1['Modello'] = 'iPhone 15'
d3['Modello'] = 'iPhone 15 (+1 anno)'
d2['Modello'] = 'iPhone 16'

# Unisci i due dataframe
df = pd.concat([d1, d2, d3])

# Plot
fig = px.line(df, x='Data', y='Prezzo', color='Modello',
              markers=False,  # se vuoi visualizzare i marker
              title='Confronto Prezzi iPhone 15 (+1 anno) vs iPhone 16')

# Personalizzazioni opzionali
#fig.update_traces(marker=dict(size=6))  # riduci la dimensione dei marker
fig.update_layout(legend=dict(font=dict(size=10)))  # riduci font della legenda
fig.update_xaxes(tickangle=45)

# Mostra il grafico
fig.show()