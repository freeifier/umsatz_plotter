import plotly.express as px
import streamlit as st

def plot(df):
    """
    Einnahmen-Pie-Chart nach Name Zahlungsbeteiligter.
    Zeigt den Gesamtbetrag über dem Plot.
    """
    einnahmen = df[df['Betrag'] > 0]
    gesamt = einnahmen['Betrag'].sum()

    st.markdown(f"**Gesamte Einnahmen: € {gesamt:,.2f}**")
    fig = px.pie(einnahmen, names='Name Zahlungsbeteiligter', values='Betrag',
                 title='Einnahmen nach Name Zahlungsbeteiligter')
    st.plotly_chart(fig)
