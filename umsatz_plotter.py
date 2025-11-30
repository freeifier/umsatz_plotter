import pandas as pd
import plotly.express as px

# CSV einlesen
datei = "Downloads/umsatz.csv"
df = pd.read_csv(datei, sep=';', decimal=',')
df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)

# Betrag in float
if df['Betrag'].dtype == object:
    df['Betrag'] = df['Betrag'].str.replace('.', '', regex=False)
    df['Betrag'] = df['Betrag'].str.replace(',', '.', regex=False).astype(float)

# Subkategorien manuell definieren
def kategorie_zuordnen(bez):
    bez = str(bez).lower()
    if any(x in bez for x in ['supermarkt','aldi','lidl','einkauf']):
        return 'Einkaufen Lebensmittel'
    elif any(x in bez for x in ['miete']):
        return 'Miete'
    elif any(x in bez for x in ['versicherung']):
        return 'Versicherungen'
    elif any(x in bez for x in ['mensa','cafeteria']):
        return 'Mensa Essen'
    else:
        return 'Sonstiges'

df['Kategorie'] = df['Bezeichnung Auftragskonto'].apply(kategorie_zuordnen)

# Einnahmen und Ausgaben trennen
einnahmen = df[df['Betrag'] > 0]
ausgaben = df[df['Betrag'] < 0]

# Einnahmen-Kuchen nach Name Zahlungsbeteiligter
fig_einnahmen = px.pie(einnahmen, names='Name Zahlungsbeteiligter', values='Betrag',
                       title='Einnahmen nach Name Zahlungsbeteiligter')
fig_einnahmen.show()

# Ausgaben-Kuchen nach Kategorie
fig_ausgaben = px.pie(ausgaben, names='Kategorie', values='Betrag',
                      title='Ausgaben nach Kategorie')
fig_ausgaben.show()

# Drilldown: Ausgaben Unterkategorien pro Kategorie
# Beispiel: interaktiv in Jupyter oder Browser
for kat in ausgaben['Kategorie'].unique():
    unterkategorien = ausgaben[ausgaben['Kategorie'] == kat].groupby('Bezeichnung Auftragskonto')['Betrag'].sum()
    fig = px.pie(names=unterkategorien.index, values=-unterkategorien.values, title=f'{kat} Unterkategorien')
    fig.show()
