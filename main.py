import streamlit as st
from pathlib import Path
import os
import importlib.util
import pandas as pd
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from loader import load_csv, save_last_file, load_last_file

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

uploaded_file = st.file_uploader("CSV-Datei wählen", type="csv")

df = None

# Neue Datei hochgeladen → temporär speichern
if uploaded_file is not None:
    tmp_path = os.path.join(TMP_DIR, uploaded_file.name)
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info(f"CSV temporär gespeichert: {tmp_path}")
    df = load_csv(tmp_path)
    save_last_file(tmp_path)

# Falls nichts hochgeladen, aber alte Datei existiert → autoload
elif (last_file := load_last_file()) and Path(last_file).exists():
    st.info(f"Letzte Datei automatisch geladen: {last_file}")
    df = load_csv(last_file)

if df is None:
    st.warning("Bitte CSV-Datei hochladen")
    st.stop()
st.write("📌 CSV-Spalten:", [repr(c) for c in df.columns])


# -------------------------------------------------------
# 🔥 Globaler Datumsbereich-Filter (NEU: Monatsbuttons)
# -------------------------------------------------------
from gui.month_selector import get_month_ranges

if "Buchungstag" not in df.columns:
    st.error("Die CSV benötigt eine Spalte 'Buchungstag'.")
    st.stop()

df["Datum"] = pd.to_datetime(df["Buchungstag"], errors="coerce")

min_date = df["Datum"].min()
max_date = df["Datum"].max()

# Neuer GUI-Selector (Monate + manuelle Eingabe)
months = get_month_ranges(min_date, max_date)
start_date = months[0][0]         # erstes Datum
end_date = months[-1][1]          # letztes Datum

# Sicherstellen, dass beide Werte gesetzt sind
if start_date is not None and end_date is not None:
    df = df[(df["Datum"] >= start_date) & (df["Datum"] <= end_date)]
    st.success(f"Zeitraum angewendet: {start_date.date()} bis {end_date.date()}")
else:
    st.warning("Bitte zwei Monate auswählen, um einen Zeitraum zu bilden.")



if df.empty:
    st.warning("Keine Daten im ausgewählten Datumsbereich.")
    st.stop()




# -------------------------------------------------------
# 🔥 Plots dynamisch laden (plot(df))
# -------------------------------------------------------
plot_dir = "plots"

for filename in os.listdir(plot_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(plot_dir, filename)
        modulname = os.path.splitext(filename)[0]
        spec = importlib.util.spec_from_file_location(modulname, filepath)
        plot_module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(plot_module)
        except Exception as e:
            st.error(f"Fehler beim Laden von Plot-Modul `{filename}`: {e}")
            continue

        if hasattr(plot_module, "plot"):
            try:
                # globaler Filter → df
                plot_module.plot(df)
            except Exception as e:
                st.error(f"Fehler im Plot `{filename}`: {e}")
                import traceback
                st.text(traceback.format_exc())
