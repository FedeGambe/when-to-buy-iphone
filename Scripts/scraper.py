import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/113.0.0.0 Safari/537.36"
}

def estrai_e_salva_prezzo(nome_prodotto, url):
    csv_path = f"Dataset/{nome_prodotto}_prize_raw.csv"

    # Caricamento CSV
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ["day_start", "day_end", "price"]] # Se ci sono colonne vuote (da virgole extra), le rimuove
    else:
        df = pd.DataFrame(columns=["day_start", "day_end", "price"])

    try: # Scraping
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        span_price = soup.find("span", class_="a-price aok-align-center reinventPricePriceToPayMargin priceToPay")
        if not span_price:
            print(f"Prezzo non trovato per {nome_prodotto}")
            return None

        whole = span_price.find("span", class_="a-price-whole").text.strip()
        fraction = span_price.find("span", class_="a-price-fraction").text.strip()
        prezzo_str = f"{whole.replace('.', '').replace(',', '')}.{fraction}"
        prezzo_float = float(prezzo_str)
        oggi = datetime.now().strftime("%d-%m-%Y")

        # Pulisce e normalizza
        df = df.dropna(subset=["day_start", "day_end", "price"])
        df["day_end"] = df["day_end"].astype(str).str.strip()
        df["price"] = df["price"].astype(float)

        #Se il DataFrame non è vuoto e il prezzo dell’ultima riga è uguale a prezzo_float
        # Allora aggiorna solo la data di fine (day_end) dell’ultima riga, mettendo oggi, il prezzo è rimasto invariato
        if not df.empty and float(df.iloc[-1]["price"]) == prezzo_float:
            df.at[df.index[-1], "day_end"] = oggi
        # Se il prezzo è diverso dall’ultimo registrato, allora crea una nuova riga
        else:
            new_row = {"day_start": oggi, "day_end": oggi, "price": prezzo_float}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        df.to_csv(csv_path, index=False)

        output = f"Aggiunto {nome_prodotto}: {oggi},{oggi},{prezzo_float}"
        print(output)
        return output

    except Exception as e:
        print(f"Errore durante scraping o aggiornamento per {nome_prodotto}: {e}")
        return None

# Lista prodotti
prodotti = [
    {"nome": "iPhone16", "url": "https://www.amazon.it/dp/B0DGJJXBM5?th=1"},
    {"nome": "iPhone15", "url": "https://www.amazon.it/Apple-iPhone-15-128-GB/dp/B0CHWV5HTM/?th=1"}
]

for prodotto in prodotti:
    estrai_e_salva_prezzo(prodotto["nome"], prodotto["url"])