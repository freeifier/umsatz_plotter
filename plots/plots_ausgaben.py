import plotly.express as px
import streamlit as st

def plot(df):
    """
    Ausgaben-Pie-Chart nach Kategorie.
    """
    ausgaben = df[df['Betrag'] < 0]
    gesamt = -ausgaben['Betrag'].sum()  # negativ -> positiver Wert

    st.markdown(f"**Gesamte Ausgaben: € {gesamt:,.2f}**")
    fig = px.pie(ausgaben, names='Name Zahlungsbeteiligter', values=-ausgaben['Betrag'],
                 title='Ausgaben nach Kategorie')
    st.plotly_chart(fig)
