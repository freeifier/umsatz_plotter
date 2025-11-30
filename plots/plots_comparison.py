import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def plot(df):
    """
    Monatsvergleich Einnahmen/Ausgaben + Differenzlinie.
    Zusätzlich: Ungegroupte Saldo-nach-Buchung-Linie über alle Transaktionen.
    """

    # Monatsspalte sicherstellen
    if "Monat" not in df.columns:
        df["Buchungstag"] = pd.to_datetime(df["Buchungstag"], dayfirst=True)
        df["Monat"] = df["Buchungstag"].dt.to_period("M")

    # Einnahmen/Ausgaben filtern
    einnahmen = df[df['Betrag'] > 0]
    ausgaben = df[df['Betrag'] < 0]

    # Gruppieren
    monat_einnahmen = einnahmen.groupby('Monat')['Betrag'].sum()
    monat_ausgaben = ausgaben.groupby('Monat')['Betrag'].sum()

    # Zusammenführen
    df_monatlich = pd.DataFrame({
        'Einnahmen': monat_einnahmen,
        'Ausgaben': monat_ausgaben
    }).fillna(0).reset_index()

    # Differenz berechnen
    df_monatlich['Differenz'] = df_monatlich['Einnahmen'] + df_monatlich['Ausgaben']

    # Sortieren nach Zeit (neu -> alt)
    df_monatlich = df_monatlich.sort_values("Monat", ascending=False)

    # Für Saldolinie: nach Buchungsdatum sortieren
    df_sorted = df.sort_values("Buchungstag")

    # Plot
    fig = go.Figure()

    # Einnahmen / Ausgaben Bars
    fig.add_bar(
        x=df_monatlich['Monat'].astype(str),
        y=df_monatlich['Einnahmen'],
        name="Einnahmen"
    )
    fig.add_bar(
        x=df_monatlich['Monat'].astype(str),
        y=df_monatlich['Ausgaben'],
        name="Ausgaben"
    )

    # Differenzlinie
    fig.add_trace(
        go.Scatter(
            x=df_monatlich['Monat'].astype(str),
            y=df_monatlich['Differenz'],
            mode="lines+markers",
            name="Differenz",
            line=dict(width=3)
        )
    )

    # 🔥 NEU: Ungegroupte Saldo-nach-Buchung-Linie
    fig.add_trace(
        go.Scatter(
            x=df_sorted['Buchungstag'],
            y=df_sorted['Saldo nach Buchung'],
            mode="lines+markers",
            name="Saldo nach Buchung",
            line=dict(width=2, dash="dot")  # dotted line
        )
    )

    fig.update_layout(
        title="Einnahmen, Ausgaben & Saldo",
        barmode="group",
        xaxis_title="Zeit",
        yaxis_title="Betrag (€)",
        legend_title="Kategorie",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Summen ausgeben
    st.markdown("### 💶 Finanzübersicht")
    st.markdown(f"**Gesamte Einnahmen:** {df_monatlich['Einnahmen'].sum():,.2f} €")
    st.markdown(f"**Gesamte Ausgaben:** {df_monatlich['Ausgaben'].sum():,.2f} €")
    st.markdown(f"**Gesamtdifferenz:** {(df_monatlich['Einnahmen'].sum() + df_monatlich['Ausgaben'].sum()):,.2f} €")
