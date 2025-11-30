import streamlit as st
from pathlib import Path
import os
import importlib.util
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


# -------------------------------------------------------
# 🔥 Globaler Datumsbereich-Filter
# -------------------------------------------------------
# Erwartet: df["Datum"] ist pandas datetime
if not "Buchungstag" in df.columns:
    st.error("Die CSV benötigt eine Spalte 'Datum'.")
    st.stop()

df["Datum"] = df["Buchungstag"].astype("datetime64[ns]")

min_date = df["Datum"].min()
max_date = df["Datum"].max()

date_range = st.date_input(
    "Datumsbereich auswählen",
    value=(min_date, max_date)
)

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["Datum"] >= str(start_date)) & (df["Datum"] <= str(end_date))]


# Falls nach dem Filter keine Daten übrig sind
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
