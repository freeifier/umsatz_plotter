import plotly.express as px
import streamlit as st
import pandas as pd
import os
import json

def plot(df):
    """
    Drilldown Ausgaben Unterkategorien zu festen Überkategorien zuordnen.
    Die Überkategorien sind vorgegeben (z.B. Lebensmitteleinkauf, Versicherungen, Mobilität).
    Jede Überkategorie hat ein Feld, in dem die Unterkategorien zugewiesen werden.
    Nicht zugewiesene Unterkategorien werden in die "Random"-Kategorie verschoben.
    Die Konfiguration wird als JSON-Datei im Unterordner 'plots_drilldown' gespeichert.
    """
    ausgaben = df[df['Betrag'] < 0]
    
    # Definierte feste Überkategorien
    ueberkategorien = ["Lebensmitteleinkauf", "Outward Essen", "Versicherungen", "Mobilität", "Miete", "Freizeit", "Gesundheit", "Random"]
    
    # Initialisiere ein Dictionary, das die Zuordnung speichert
    if 'subcategory_to_category' not in st.session_state:
        st.session_state['subcategory_to_category'] = {k: [] for k in ueberkategorien}

    # Liste für bereits ausgewählte Unterkategorien
    selected_subcategories_all = []
    
    # Für jede Überkategorie ein Auswahlfeld anzeigen
    for ueberkategorie in ueberkategorien:
        st.write(f"**{ueberkategorie}**:")
        
        # Unterkategorien (aus den Ausgaben) aus den Daten extrahieren, die zu dieser Überkategorie zugeordnet werden können
        possible_subcategories = ausgaben['Name Zahlungsbeteiligter'].unique()
        
        # Entfernen der bereits ausgewählten Unterkategorien aus der Auswahl für das aktuelle Feld
        available_subcategories = [subcat for subcat in possible_subcategories if subcat not in selected_subcategories_all]
        
        # Vorbelegen der bereits ausgewählten Unterkategorien
        if ueberkategorie in st.session_state['subcategory_to_category']:
            selected_subcategories = st.multiselect(
                f"Welche Unterkategorien gehören zu {ueberkategorie}?", 
                available_subcategories,
                default=st.session_state['subcategory_to_category'][ueberkategorie],
                key=ueberkategorie
            )
        else:
            selected_subcategories = st.multiselect(
                f"Welche Unterkategorien gehören zu {ueberkategorie}?", 
                available_subcategories,
                key=ueberkategorie
            )
        
        # Speichern der ausgewählten Unterkategorien für diese Überkategorie
        st.session_state['subcategory_to_category'][ueberkategorie] = selected_subcategories
        selected_subcategories_all.extend(selected_subcategories)
    
    # Zuordnung der nicht ausgewählten Unterkategorien in die "Random"-Kategorie
    all_subcategories = set(ausgaben['Name Zahlungsbeteiligter'].unique())
    unassigned_subcategories = all_subcategories - set(selected_subcategories_all)
    st.session_state['subcategory_to_category']["Random"].extend(unassigned_subcategories)
    
    # Speichern der Zuordnung als JSON-Datei
    save_json(st.session_state['subcategory_to_category'])
    
    # Speichern der Zuordnung als Preset im Session State
    if st.button("Preset speichern"):
        st.success("Preset gespeichert!")
    
    # Zeige gespeicherte Zuordnungen, falls vorhanden
    if "saved_category_mapping" in st.session_state:
        st.write("Gespeicherte Zuordnungen:")
        st.write(st.session_state.saved_category_mapping)
        subcategory_to_category = st.session_state.saved_category_mapping
    
    # Zuordnung der Unterkategorien zu den Überkategorien
    ausgaben['Überkategorie'] = 'Nicht zugeordnet'
    
    for ueberkategorie, subcats in st.session_state['subcategory_to_category'].items():
        ausgaben.loc[ausgaben['Name Zahlungsbeteiligter'].isin(subcats), 'Überkategorie'] = ueberkategorie
    
    # Filtern der Ausgaben, die einer Überkategorie zugewiesen wurden
    filtered_ausgaben = ausgaben[ausgaben['Überkategorie'] != 'Nicht zugeordnet']
    
    # Gruppieren nach Überkategorie
    grouped = filtered_ausgaben.groupby('Überkategorie')['Betrag'].sum()

    # Erstellen des Pie-Charts
    fig = px.pie(grouped, names=grouped.index, values=-grouped.values,
                 title="Ausgaben nach Überkategorien")
    st.plotly_chart(fig)

def save_json(category_mapping):
    """
    Speichert die Zuordnung der Unterkategorien zu den Überkategorien in einer JSON-Datei im Unterordner 'plots_drilldown'.
    """
    # Pfad zum Unterordner
    output_dir = "plots_drilldown"
    
    # Überprüfen, ob der Ordner existiert, andernfalls erstellen
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Pfad zur JSON-Datei
    json_file_path = os.path.join(output_dir, "category_mapping.json")
    
    # Speichern der Zuordnung als JSON-Datei
    with open(json_file_path, "w") as f:
        json.dump(category_mapping, f, indent=4)
    st.success(f"Konfiguration wurde in '{json_file_path}' gespeichert.")
