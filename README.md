# When to buy iphone

IN PROGRESS

è uno programma Python che analizza e prevede l’andamento dei prezzi degli iPhone nel tempo, aiutando a individuare il momento migliore per l’acquisto. Il progetto utilizza dati storici provenienti da Keepa e integra uno scraper per monitorare i prezzi in tempo reale.

---

## Descrizione del progetto

Il progetto parte da una fase di inserimento dei dati (data entry), in cui i prezzi storici degli iPhone analizzati su Keepa vengono importati manualmente. È inoltre incluso un modulo di scraping automatico, che consente di rilevare in tempo reale il prezzo attuale degli iPhone da Amazon (o altri store compatibili), senza necessità di intervento manuale.

Successivamente, i dati vengono **processati**:
- Viene calcolato il **trimestre di riferimento** (rispetto alla data di rilascio del modello)
- Si calcolano i **giorni passati dal lancio** del dispositivo

Questi dati temporali sono poi utilizzati per:
- Analizzare l’**andamento dei prezzi nel tempo**
- Evidenziare eventuali pattern di ribasso
- Effettuare una **previsione dei prezzi** per i mesi successivi tramite modelli di regressione o serie temporali


---

## Funzionalità
- 📥 Importazione dati manuali da Keepa o in maniera automatica con Scraping del prezzo attuale
- 🧮 Calcolo del trimestre e dei giorni dal lancio
- 📊 Analisi dell’andamento storico dei prezzi
- 🔮 Previsioni sui prezzi futuri
- 📈 Visualizzazioni grafiche intuitive

---

## Struttura

```
data/        CSV dei prezzi (day_start, day_end, price), uno per modello
src/         codice
  esporta.py   script: esporta PNG e pagina HTML interattiva in analisi/
  scraper.py   script: prezzo attuale da Amazon
  utils/       funzioni riusabili
    dati.py      caricamento e preparazione dei dati (carica_modello)
    calcoli.py   calcoli dell'analisi (sconti, minimi, stagionalità, offerte...)
    grafici.py   grafici plotly
analisi/     report: notebook price_comparison, ANALISI_PREZZI.md, img/, analisi.html
Notebook/    previsioni (Prophet, SARIMAX)
```
