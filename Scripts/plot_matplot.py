import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

d1 = pd.read_csv("iphone15.csv")
d2 = pd.read_csv("iphone16.csv")

d1['Data'] = pd.to_datetime(d1['Data'])
d2['Data'] = pd.to_datetime(d2['Data'])

d1['Data'] = d1['Data'] + pd.DateOffset(years=1)

plt.figure()
plt.plot(d1['Data'], d1['Prezzo'], label='iPhone 15 (+1 anno)')  # ← niente marker
plt.plot(d2['Data'], d2['Prezzo'], label='iPhone 16')            # ← niente marker
plt.xlabel('Data')
plt.ylabel('Prezzo (€)')
plt.title('Confronto Prezzi iPhone 15 (+1 anno) vs iPhone 16')
plt.xticks(rotation=45)
plt.legend(prop={'size': 8})
plt.tight_layout()
plt.grid()

plt.show()