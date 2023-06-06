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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
#Page config
st.set_page_config(
    page_title='Paris pollution',
    page_icon='🚍🚙',
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

st.title("Lets have a look at Paris air quality !")
st.write("thanks to Airparif API, we can have a look at the air quality in Paris with only 2hours of delay !")
path = r"C:\Users\Oswald Benoit\Desktop\PSB\cours\Business_Intelligence\streamlit_Paris_Respire\data\secteurs-paris-respire.csv"
df = pd.read_csv(path, delimiter=';')
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

# Création d'un nouveau dataframe df2 qui récupère la data de l'api Airparif
from datetime import datetime, timedelta
heure_actuelle = datetime.now()
heure_precedente = heure_actuelle.replace(minute=0, second=0, microsecond=0)
heure_terminée = heure_precedente - timedelta(hours=2)
heure_terminée_str = heure_terminée.strftime("%Y-%m-%dT%H:%M:%SZ")
#print(heure_terminée_str)

# URL de l'API
url = "https://api.airparif.asso.fr/horair/historique"

# Clé d'accès
api_key = "e0553c24-e9e9-c7c4-60bf-207e71a9933f"

# Création d'un nouveau dataframe df2
df2 = df.copy()  # Copie toutes les colonnes de df dans df2

# Ajout des colonnes d'indice et de PM10 à df2
df2["indice"] = None
df2["pm10"] = None

# Date du jour précédent
previous_date = datetime.now() - relativedelta(days=1)
previous_date_str = previous_date.strftime("%Y-%m-%dT%H:%M:%SZ")
Date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

# Itération sur les lignes du dataframe
for index, row in df.iterrows():
    # Récupération des coordonnées
    longitude = row["longitude"]
    latitude = row["latitude"]

    # Paramètres de la requête POST
    params = {
        "polluants": ["indice", "pm10"],
        "longitude": longitude,
        "latitude": latitude,
        "datemax": heure_terminée_str,
        "heures": 1
    }

    # En-têtes de la requête
    headers = {
        "X-Api-Key": api_key
    }

    # Effectuer la requête POST à l'API
    response = requests.post(url, json=params, headers=headers)

    # Vérifier si la requête a réussi (code d'état 200)
    if response.status_code == 200:
        # Extraire les données JSON de la réponse
        data = response.json()

        # Récupérer les valeurs d'indice et de PM10
        indice = data["valeurs"]["indice"][0] if data["valeurs"]["indice"] else None
        pm10 = data["valeurs"]["pm10"][0] if data["valeurs"]["pm10"] else None

        # Assigner les valeurs aux colonnes correspondantes dans df2
        df2.at[index, "indice"] = indice
        df2.at[index, "pm10"] = pm10

    else:
        # La requête a échoué
        st.write(f"La requête a échoué pour la paire de coordonnées ({longitude}, {latitude}) avec le code d'état:", response.status_code)



#
## Création d'un nouveau dataframe df3 avec une coordoonée par arrondissement dans paris
#data = {
#    'Arrondissement': ['1er', '2e', '3e', '4e', '5e', '6e', '7e', '8e', '9e', '10e',
#                        '11e', '12e', '13e', '14e', '15e', '16e', '17e', '18e', '19e', '20e'],
#    'Latitude': [48.85, 48.86, 48.86, 48.85, 48.84, 48.84, 48.85, 48.87, 48.87, 48.87,
#                 48.86, 48.83, 48.82, 48.83, 48.84, 48.86, 48.88, 48.89, 48.88, 48.86],
#    'Longitude': [2.34, 2.34, 2.36, 2.35, 2.34, 2.33, 2.32, 2.31, 2.33, 2.36,
#                  2.37, 2.44, 2.36, 2.32, 2.29, 2.26, 2.32, 2.34, 2.38, 2.39]
#}
#
#df3 = pd.DataFrame(data)
##création d'un df4 qui récupère la data de l'api Airparif et la joint aux info de df3 
## URL de l'API
#url = "https://api.airparif.asso.fr/horair/historique"
#
## Clé d'accès
#api_key = "e0553c24-e9e9-c7c4-60bf-207e71a9933f"
#
## Création d'un nouveau dataframe df2
#df4 = df3.copy()  # Copie toutes les colonnes de df dans df2
#
## Ajout des colonnes d'indice et de PM10 à df2
#df4["indice"] = None
#df4["pm10"] = None
#
## Date du jour précédent
#previous_date = datetime.now() - relativedelta(days=1)
#previous_date_str = previous_date.strftime("%Y-%m-%dT%H:%M:%SZ")
#Date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
#
#
## Itération sur les lignes du dataframe
#for index, row in df3.iterrows():
#    # Récupération des coordonnées
#    longitude = row["Longitude"]
#    latitude = row["Latitude"]
#
#    # Paramètres de la requête POST
#    params = {
#        "polluants": ["indice", "pm10"],
#        "longitude": longitude,
#        "latitude": latitude,
#        "datemax": heure_terminée_str,
#        "heures": 1
#    }
#
#    # En-têtes de la requête
#    headers = {
#        "X-Api-Key": api_key
#    }
#
#    # Effectuer la requête POST à l'API
#    response = requests.post(url, json=params, headers=headers)
#
#    # Vérifier si la requête a réussi (code d'état 200)
#    if response.status_code == 200:
#        # Extraire les données JSON de la réponse
#        data = response.json()
#
#        # Récupérer les valeurs d'indice et de PM10
#        indice = data["valeurs"]["indice"][0] if data["valeurs"]["indice"] else None
#        pm10 = data["valeurs"]["pm10"][0] if data["valeurs"]["pm10"] else None
#
#        # Assigner les valeurs aux colonnes correspondantes dans df2
#        df4.at[index, "indice"] = indice
#        df4.at[index, "pm10"] = pm10
#
#    else:
#        # La requête a échoué
#        st.write(f"La requête a échoué pour la paire de coordonnées ({longitude}, {latitude}) avec le code d'état:", response.status_code)
#

#je récupère un csv de tous les arrondissement de paris avec les bonnes coordonnées
path2 = r"C:\Users\Oswald Benoit\Desktop\PSB\cours\Business_Intelligence\streamlit_Paris_Respire\data\arrondissements.csv"
df9 = pd.read_csv(path2, delimiter = ';') #Using delimiter for identifying the different columns
df9[['latitude', 'longitude']] = df9['geom_x_y'].str.split(',', expand=True)

#créer un dataframe avec les colonnes qui nous intéressent
# URL de l'API
url = "https://api.airparif.asso.fr/horair/historique"

# Clé d'accès
api_key = "e0553c24-e9e9-c7c4-60bf-207e71a9933f"

# Création d'un nouveau dataframe df2
df5 = df9.copy()  # Copie toutes les colonnes de df dans df2

# Ajout des colonnes d'indice et de PM10 à df2
df5["indice"] = None
df5["pm10"] = None

# Date du jour précédent
previous_date = datetime.now() - relativedelta(days=1)
previous_date_str = previous_date.strftime("%Y-%m-%dT%H:%M:%SZ")
Date_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


# Itération sur les lignes du dataframe
for index, row in df9.iterrows():
    # Récupération des coordonnées
    longitude = row["longitude"]
    latitude = row["latitude"]

    # Paramètres de la requête POST
    params = {
        "polluants": ["indice", "pm10"],
        "longitude": longitude,
        "latitude": latitude,
        "datemax": heure_terminée_str,
        "heures": 1
    }

    # En-têtes de la requête
    headers = {
        "X-Api-Key": api_key
    }

    # Effectuer la requête POST à l'API
    response = requests.post(url, json=params, headers=headers)

    # Vérifier si la requête a réussi (code d'état 200)
    if response.status_code == 200:
        # Extraire les données JSON de la réponse
        data = response.json()

        # Récupérer les valeurs d'indice et de PM10
        indice = data["valeurs"]["indice"][0] if data["valeurs"]["indice"] else None
        pm10 = data["valeurs"]["pm10"][0] if data["valeurs"]["pm10"] else None

        # Assigner les valeurs aux colonnes correspondantes dans df2
        df5.at[index, "indice"] = indice
        df5.at[index, "pm10"] = pm10

    else:
        # La requête a échoué
       st.write(f"La requête a échoué pour la paire de coordonnées ({longitude}, {latitude}) avec le code d'état:", response.status_code)

#df5.head(20)
import requests
import json

paris_geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/departements/75-paris/communes-75-paris.geojson'
response = requests.get(paris_geojson_url)
paris_geojson = response.json()

for feature in paris_geojson['features']:
    code = feature['properties']['code']
    for index, row in df5.iterrows():
        insee = str(row['c_arinsee'])
        if insee == code:
            indice = row['indice']
            pm10 = row['pm10']
            feature['properties']['indice'] = indice
            feature['properties']['pm10'] = pm10

with open('nouveau_data.geojson', 'w') as f:
    json.dump(paris_geojson, f)


#for feature in paris_geojson['features']:
#    properties = feature['properties']
#    for key, value in properties.items():
#        print(f"{key}: {value}")
#    print("\n")
import folium
from branca.colormap import LinearColormap

# Créer une carte centrée sur Paris
map_paris_indice = folium.Map(location=[48.859, 2.347], zoom_start=12)

# Définir les couleurs du gradient
start_color = 'green'
medium_color = 'yellow'
end_color = 'red'

# Définir les limites pour la différence PM10 - 100
diff_min = 0
diff_max = 50

# Créer le colormap avec le gradient progressif
cmap = LinearColormap(colors=[start_color, medium_color, end_color], vmin=diff_min, vmax=diff_max, caption='Indice global de pollution')

# Ajouter la légende à la carte
map_paris_indice.add_child(cmap)

# Itérer sur les fonctionnalités du GeoJSON
for feature in paris_geojson['features']:
    properties = feature['properties']
    nom = properties['nom']
    indice = properties['indice']
    pm10 = properties['pm10']
    
    # Calculer la différence indice 
    difference = indice
    
    # Obtenir la couleur en utilisant le gradient
    color = cmap(difference)
    
    # Convertir la couleur en format hexadécimal
    color_hex = color
    border_color_hex = '#808080'  # Couleur des bordures (gris)
    border_weight = 2  # Épaisseur des bordures en pixels

    # Ajouter une couche de polygone à la carte pour chaque fonctionnalité
    folium.GeoJson(
        feature,
        style_function=lambda x: {'fillColor': color_hex, 'color': border_color_hex, 'weight': border_weight},
        tooltip=f"Nom: {nom}<br>Indice: {indice}<br>PM10: {pm10}"
    ).add_to(map_paris_indice)

# Afficher la carte
st.subheader("Indice de pollution global en direct par arrondissement de Paris")
folium_static(map_paris_indice)
#map_paris_indice

import folium
from branca.colormap import LinearColormap

# Créer une carte centrée sur Paris
map_paris_pm10= folium.Map(location=[48.859, 2.347], zoom_start=12)

# Définir les couleurs du gradient
start_color = 'green'
medium_color = 'yellow'
end_color = 'red'

# Définir les limites pour la différence PM10 - 100
diff_min = 0
diff_max = 70

# Créer le colormap avec le gradient progressif
cmap = LinearColormap(colors=[start_color, medium_color, end_color], vmin=diff_min, vmax=diff_max, caption='Indice des particules fines PM10')

# Ajouter la légende à la carte
map_paris_pm10.add_child(cmap)

# Itérer sur les fonctionnalités du GeoJSON
for feature in paris_geojson['features']:
    properties = feature['properties']
    nom = properties['nom']
    indice = properties['indice']
    pm10 = properties['pm10']
    
    # Calculer la différence indice 
    difference = pm10
    
    # Obtenir la couleur en utilisant le gradient
    color = cmap(difference)
    
    # Convertir la couleur en format hexadécimal
    color_hex = color
    border_color_hex = '#808080'  # Couleur des bordures (gris)
    border_weight = 2  # Épaisseur des bordures en pixels

    # Ajouter une couche de polygone à la carte pour chaque fonctionnalité
    folium.GeoJson(
        feature,
        style_function=lambda x: {'fillColor': color_hex, 'color': border_color_hex, 'weight': border_weight},
        tooltip=f"Nom: {nom}<br>Indice: {indice}<br>PM10: {pm10}"
    ).add_to(map_paris_pm10)

# Afficher la carte
st.subheader("Polution particule fines en direct par arrondissement de Paris")
folium_static(map_paris_pm10)
