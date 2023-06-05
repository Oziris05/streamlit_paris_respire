import streamlit as st
import pandas as pd
import folium
import json
import datetime
import holidays
import locale

st.title("Analyse de la qualité de l'air à Paris")

# Charger les données des secteurs Paris Respire
path = r"C:\Users\Oswald Benoit\Desktop\PSB\cours\Business_Intelligence\streamlit_Paris_Respire\data\secteurs-paris-respire.csv"
df = pd.read_csv(path, delimiter=';')
Geoson_dataset = "https://www.data.gouv.fr/fr/datasets/r/0d20c007-3956-4cff-bf52-d0d2e2d6d56d"
# Afficher les 5 premières lignes du DataFrame
st.subheader("Aperçu des données")
st.dataframe(df.head())

# Prétraitement des données
df[['latitude', 'longitude']] = df['geo_point_2d'].str.split(',', expand=True)

jours_format_liste = [
    'dimanche,férié',
    'dimanche',
    'dimanche,férié',
    '1dimanche',
    'dimanche,férié',
    'dimanche,férié',
    'dimanche,férié',
    'dimanche,férié',
    'samedi,dimanche,férié',
    'dimanche,férié',
    'dimanche,férié',
    '1dimanche',
    'dimanche',
    'dimanche,férié',
    'dimanche,férié',
    'dimanche,férié',
    'dimanche',
    'dimanche,férié',
    'dimanche,férié',
    'samedi,dimanche,férié',
    'dimanche,férié',
    'dimanche',
    'samedi,dimanche',
    'dimanche,férié',
    'dimanche,férié',
    'samedi,dimanche',
    'dimanche,férié'
]
df['jours_format'] = pd.Series(jours_format_liste)

def extraire_plage_horaire(horaire):
    if isinstance(horaire, str):
        horaire = horaire.lower()
        horaire = horaire.replace('de ', '').replace('h', '').replace(' ', '').replace('/', '-')
        horaires_separes = horaire.split('/')
        plages_horaires = []
        for plage in horaires_separes:
            if plage != 'nan':
                if 'à' in plage:
                    debut, fin = plage.split('à')
                    plages_horaires.append(f'{debut}-{fin}')
                else:
                    plages_horaires.append(plage)
        plage_horaire_format = ' / '.join(plages_horaires)
        return plage_horaire_format
    else:
        return ""

df["plage_horaire_format"] = df["horaires_annee"].apply(extraire_plage_horaire)

def get_plage_horaire(plage_horaire):
    if isinstance(plage_horaire, str):
        heures = plage_horaire.split("-")
        if len(heures) == 2:
            debut = int(heures[0].strip())
            fin = int(heures[1].strip())
            return debut, fin
    return None

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
fr_holidays = holidays.FRA()
aujourd_hui = datetime.datetime.now()
jour_semaine = aujourd_hui.strftime("%A")
heure_ = aujourd_hui.hour
minute = aujourd_hui.minute
seconde = aujourd_hui.second
heure_int = heure_ + minute / 60 + seconde / 3600

def jour_inclus(jour, plage_jours):
    if "dimanche" in plage_jours and jour == "dimanche":
        return True
    elif "férié" in plage_jours and aujourd_hui in fr_holidays:
        return True
    elif "samedi" in plage_jours and jour == "samedi":
        return True
    elif "1dimanche" in plage_jours and jour == "dimanche" and aujourd_hui.day < 7:
        return True
    else:
        return False

# Créer une carte centrée sur Paris
paris_map = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Charger le jeu de données des quartiers parisiens
folium.GeoJson(path, name="geo_shape").add_to(paris_map)

# Ajouter un marqueur pour chaque quartier
for index, row in df.iterrows():
    quartier = row["nom"]
    arrondissement = row["arrdt"]
    latitude = row["latitude"]
    longitude = row["longitude"]
    plage_horaire = row["plage_horaire_format"]
    plage_jours = row["jours_format"]
    plage_horaire_values = get_plage_horaire(plage_horaire)
    if plage_horaire_values is not None:
        debut, fin = plage_horaire_values
        jour_inclu = jour_inclus(jour_semaine, plage_jours)
        if jour_inclu and debut <= heure_int <= fin:
            color = 'red'
        else:
            color = 'green'
        folium.CircleMarker(location=[latitude, longitude], radius=10, color=color, tooltip=f"{quartier}, {arrondissement}").add_to(paris_map)
        folium.Marker(location=[latitude, longitude], icon=folium.Icon(color=color), tooltip=f"{quartier}, {arrondissement}").add_to(paris_map)

# Afficher la carte
st.subheader("Carte des zones Paris Respire")
st.write(paris_map._repr_html_(), unsafe_allow_html=True)
