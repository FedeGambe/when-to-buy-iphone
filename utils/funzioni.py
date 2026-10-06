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

from sklearn.linear_model import LinearRegression
import numpy as np
def prezzo_trimestri_stats(df):
    if not pd.api.types.is_datetime64_any_dtype(df['Data']):
        df = df.copy()
        df['Data'] = pd.to_datetime(df['Data'])
    
    prezzi = df['Prezzo']
    cambio_prezzo = prezzi.iloc[-1] - prezzi.iloc[0]
    max_calo = prezzi.max() - prezzi.min()
    volatilita = prezzi.std()
    
    # Trend lineare
    X = np.arange(len(prezzi)).reshape(-1, 1)
    y = prezzi.values.reshape(-1, 1)
    model = LinearRegression().fit(X, y)
    trend = model.coef_[0][0]
    
    # Giorni in crescita e in calo
    variazioni = prezzi.diff().dropna()
    giorni_up = (variazioni > 0).sum()
    giorni_down = (variazioni < 0).sum()

    return pd.Series({
        #'Prezzo Medio': round(prezzi.mean(), 2),
        'Prezzo Mediano': round(prezzi.median(), 2),
        'Prezzo Minimo': round(prezzi.min(), 2),
        'Prezzo Massimo': round(prezzi.max(), 2),
        'Oscillazione Massima (€)': round(max_calo, 2),
        'Range (%)': round((max_calo / prezzi.mean()) * 100, 2),
        'Volatilità (std dev)': round(volatilita, 2),
        'Trend Lineare (€/giorno)': round(trend, 4),
        'Giorni in Crescita': giorni_up,
        'Giorni in Calo': giorni_down
    })
    
