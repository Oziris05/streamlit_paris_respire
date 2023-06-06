import streamlit as st
import pandas as pd
import folium
import json
import datetime
import holidays
import locale
from streamlit_folium import folium_static
import requests
import json
st.set_page_config(
    page_title='Breathing Areas in paris',
    page_icon='🚴‍♂️🌳',
    layout='wide',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an extremely cool app!"
    })

# Side bar
with st.sidebar:
    st.header('Informations on author')
    st.markdown('**Oswald BENOIT💻**')
    st.write('📈Data manager at ENGIE HOME SERVICE | Data Management student at EFREI Paris🗼') 
    st.write("""<div style="width:100%;text-align:center;"><a href="https://www.linkedin.com/in/oswald-benoit-a951a817b/" style="float:center"><img src="https://img.shields.io/badge/Oswald%20BENOIT-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/oswald-benoit-a951a817b/%22" width="100%" height="50%"></img></a></div>""", unsafe_allow_html=True)

st.title("Which zone are concerned by Paris Respire right now or in the following days of the week?")
# Charger les données des secteurs Paris Respire
path = r"C:\Users\Oswald Benoit\Desktop\PSB\cours\Business_Intelligence\streamlit_Paris_Respire\data\secteurs-paris-respire.csv"
df = pd.read_csv(path, delimiter=';')
geojson_path = "https://www.data.gouv.fr/fr/datasets/r/0d20c007-3956-4cff-bf52-d0d2e2d6d56d"
# Afficher les 5 premières lignes du DataFrame
st.subheader("Quick look at the data")
st.dataframe(df.head())
st.write("In order to create the map you will see below, I had to modified the dataframe, for example I created a new column with the time range in 10-18 format rather than 10am to 6pm.")
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
    'samedi',
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
# Liste des jours de la semaine
jours_semaine_list = ["lundi","mardi","mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
#obtenir l'heure actuelle
heure_actuelle = datetime.datetime.now().time()
# Interface utilisateur avec Streamlit
jour_selectionne = st.selectbox("Choisissez un jour de la semaine", jours_semaine_list)
# Convertir le jour sélectionné en indice
now = datetime.datetime.now()
indice_jour = now.weekday()
jour_index = jours_semaine_list.index(jour_selectionne) - (indice_jour+1)  

#aujourd_hui = datetime.datetime.now().replace(
#    day=jour_index,
#    hour=heure_actuelle.hour,
#    minute=heure_actuelle.minute,
#    second=heure_actuelle.second
#)
#st.write(aujourd_hui)
jour_semaine =jour_selectionne #aujourd_hui.strftime("%A")
#st.write(jour_semaine)
heure_ = now.hour
minute = now.minute
seconde = now.second
heure_int = heure_ + minute / 60 + seconde / 3600

def jour_inclus(jour, plage_jours):
    if "dimanche" in plage_jours and jour == "dimanche":
        return True
    elif "férié" in plage_jours and now in fr_holidays:
        return True
    elif "samedi" in plage_jours and jour == "samedi":
        return True
    elif "1dimanche" in plage_jours and jour == "dimanche":# and now.day < 7:
        return True
    else:
        return False

# Créer une carte centrée sur Paris
paris_map = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

# Charger le jeu de données des quartiers parisiens
folium.GeoJson(geojson_path, name="geo_shape").add_to(paris_map)

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
folium_static(paris_map)
# Page config
