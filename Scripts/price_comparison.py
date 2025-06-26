import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from funzioni import processa_df, trimestri_stats, prezzo_trimestri_stats, assegna_quadrimestre

# -------------------------------
# Lettura e preparazione dati
# -------------------------------

iphone15 = pd.read_csv("iPhone15.csv")
iphone16 = pd.read_csv("iPhone16.csv")
combined = pd.concat([iphone15, iphone16], ignore_index=True)

stats_15 = trimestri_stats(iphone15, "iPhone15")
stats_16 = trimestri_stats(iphone16, "iPhone16")
df_statistiche = pd.concat([stats_15, stats_16], ignore_index=True)

# Ordine trimestri e aggiunta colonna Trimestre "Q..."
ordine_trimestri = ['Q1', 'Q2', 'Q3', 'Q4']
df_statistiche['Trimestre'] = pd.Categorical(df_statistiche['Trimestre'], categories=ordine_trimestri, ordered=True)
# Calcolo giorno medio per trimestre per plotting 
trimestre_to_giorni = {'Q1': (0, 90),'Q2': (91, 180),'Q3': (181, 270),'Q4': (271, 365)}
df_statistiche['Giorni_dal_lancio'] = df_statistiche['Trimestre'].map(lambda q: sum(trimestre_to_giorni[q]) // 2)

# Colori
palette = {'iPhone15': 'red','iPhone16': 'blue'}
trimestre_color = {
    'Q1': '#D1E8FF',
    'Q2': '#DFFFD1',
    'Q3': '#FFEAD1',
    'Q4': '#F3D1FF'
}

# -------------------------------
# Plotting con GridSpec
# -------------------------------
fig = plt.figure(figsize=(20, 12))
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1.2])

# --- Plot 1: Prezzo nel primo anno ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(iphone15['Giorni_dal_lancio'], iphone15['Prezzo'], label='iPhone 15', color='red')
ax1.plot(iphone16['Giorni_dal_lancio'], iphone16['Prezzo'], label='iPhone 16', color='blue')
ax1.set_title('Prezzo nel Primo Anno')
ax1.set_xlabel('Giorni dal Lancio')
ax1.set_ylabel('Prezzo (€)')
ax1.grid(True)
ax1.legend()

# --- Plot 2: Prezzo medio per trimestre ---
ax2 = fig.add_subplot(gs[0, 1])
for modello in df_statistiche['Modello'].unique():
    df_mod = df_statistiche[df_statistiche['Modello'] == modello]
    ax2.plot(df_mod['Trimestre'], df_mod['mean'], marker='o', label=modello, color=palette[modello])
ax2.set_title('Prezzo Medio per Trimestre')
ax2.set_ylabel('Prezzo Medio (€)')
ax2.grid(True)
ax2.legend()

# --- Plot 3: Prezzi giornalieri + medi con aree Q ---
ax3 = fig.add_subplot(gs[1, :])
for trimestre, (start, end) in trimestre_to_giorni.items():
    ax3.axvspan(start, end, color=trimestre_color[trimestre], alpha=0.3)
    ax3.text((start + end) / 2, df_statistiche['mean'].max() * 1.02, trimestre,
             ha='center', va='top', fontsize=10, color='gray', alpha=0.7)

# Prezzi giornalieri
for modello in combined['Modello'].unique():
    df_comb = combined[combined['Modello'] == modello]
    ax3.plot(df_comb['Giorni_dal_lancio'], df_comb['Prezzo'], alpha=0.5,
             label=f'{modello} giornaliero', color=palette[modello], linewidth=1)

# Prezzi medi trimestrali
for modello in df_statistiche['Modello'].unique():
    df_mod = df_statistiche[df_statistiche['Modello'] == modello]
    ax3.plot(df_mod['Giorni_dal_lancio'], df_mod['mean'], marker='o',
             label=f'{modello} medio', color=palette[modello], linewidth=2)

    for _, row in df_mod.iterrows():
        ax3.text(row['Giorni_dal_lancio'], row['mean'] + 5, f"{row['mean']:.0f}€",
                 ha='center', fontsize=8, color=palette[modello])

ax3.set_title('Prezzi Giornalieri + Prezzi Medi Trimestrali')
ax3.set_xlabel('Giorni dal Lancio')
ax3.set_ylabel('Prezzo (€)')
ax3.grid(True)
ax3.legend(ncol=2, fontsize=9)

plt.tight_layout()
plt.show()

# -------------------------------
# Statistiche Riassuntive finali
# -------------------------------
resoconto_q = combined.groupby(['Modello', 'Trimestre'], observed=True).apply(
    prezzo_trimestri_stats, include_groups=False
).reset_index()

print(resoconto_q)