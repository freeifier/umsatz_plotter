import pandas as pd
import os
import json
from pathlib import Path

CONFIG_FILE = os.path.join("src", "loader_config.json")  # speichert den letzten Pfad

def save_last_file(file_path):
    """Speichert den zuletzt verwendeten Dateipfad (nur wenn str, nicht UploadedFile)"""
    
    config = {"last_file": file_path}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_last_file():
    """Gibt den zuletzt verwendeten Dateipfad zurück, falls vorhanden"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            last_file = config.get("last_file")
            if last_file and Path(last_file).exists():
                return last_file
    return None

def load_csv(file):
    """
    CSV einlesen und vorbereiten:
    - Betrag als float
    - Buchungstag als datetime
    - Monatsspalte hinzufügen
    """
    df = pd.read_csv(file, sep=';', decimal=',')
    df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)

    # Betrag float konvertieren
    if df['Betrag'].dtype == object:
        df['Betrag'] = df['Betrag'].str.replace('.', '', regex=False)
        df['Betrag'] = df['Betrag'].str.replace(',', '.', regex=False).astype(float)

    # Monatsspalte hinzufügen
    df['Monat'] = df['Buchungstag'].dt.to_period('M')

    # Nur speichern, wenn es ein richtiger Pfad ist (str), nicht UploadedFile
    if isinstance(file, str):
        save_last_file(file)

    return df
