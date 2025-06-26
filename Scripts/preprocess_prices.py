from datetime import datetime, timedelta
import pandas as pd
from funzioni import processa_df, df_espanso
import os

products = [
    "iPhone15", 
    "iPhone16"
]

for product in products:
    input_file = f"Dataset/{product}_prize_raw.csv"
    output_file = f"Dataset/{product}.csv"
    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
        continue
    try:
        df = pd.read_csv(input_file)
        expanded_rows = df_espanso(df)
        df_expanded = pd.DataFrame(expanded_rows)
        df_procesed = processa_df(df_expanded, product)
        df_procesed.sort_values(by="Data", inplace=True)
        df_procesed.to_csv(output_file, index=False)
        print(f"✅ {len(df_procesed)} righe salvate in '{output_file}'")
    except Exception as e:
        print(f"❌ Errore durante il processing di {product}: {e}")