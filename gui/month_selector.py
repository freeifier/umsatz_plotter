import streamlit as st
import pandas as pd
import calendar

st.set_page_config(page_title="Monatsauswahl", layout="wide")

# -----------------------------
# Hilfsfunktion: Monatsstart-Ende
# -----------------------------
def get_month_ranges(min_date, max_date):
    cur = pd.Timestamp(min_date.year, min_date.month, 1)
    ranges = []
    while cur <= max_date:
        start = cur
        end = cur + pd.offsets.MonthEnd(1)
        ranges.append((start, end))
        cur = cur + pd.DateOffset(months=1)
    return ranges

# -----------------------------
# Session State initialisieren
# -----------------------------
if "selected_months" not in st.session_state:
    st.session_state.selected_months = []

# -----------------------------
# CSS für Buttons
# -----------------------------
st.markdown("""
<style>
.month-btn {
    margin: 4px;
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid #888;
    font-weight: 600;
    cursor: pointer;
    transition: 0.2s;
}
.month-btn:hover {
    background-color: #ddd;
}
.month-selected {
    background-color: #4a90e2;
    color: white;
    border-color: #2a70c2;
}
.month-row {
    display: flex;
    flex-wrap: wrap;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Zeitraum für die Buttons definieren
# -----------------------------
min_date = pd.Timestamp("2025-11-01")
max_date = pd.Timestamp("2026-02-28")
months = get_month_ranges(min_date, max_date)  # <-- WICHTIG

# -----------------------------
# Anzeige nach Jahr gruppiert
# -----------------------------
years = {}
for start, end in months:
    years.setdefault(start.year, []).append((start, end))

for year, items in years.items():
    st.markdown(f"### {year}")
    cols = st.columns(len(items))
    for col, (start, end) in zip(cols, items):
        label = calendar.month_name[start.month][:3]
        is_selected = start in st.session_state.selected_months
        css_class = "month-btn month-selected" if is_selected else "month-btn"

        # Button klickbar
        with col:
            if st.button(label, key=f"{year}-{start.month}"):
                if is_selected:
                    st.session_state.selected_months.remove(start)
                else:
                    if len(st.session_state.selected_months) < 2:
                        st.session_state.selected_months.append(start)

# -----------------------------
# Rückgabe der Range
# -----------------------------
if len(st.session_state.selected_months) == 2:
    m1, m2 = sorted(st.session_state.selected_months)
    st.success(f"Ausgewählte Range: {m1.date()} → {m2 + pd.offsets.MonthEnd(1)}")
else:
    st.info("Bitte genau 2 Monate auswählen")
