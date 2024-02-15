import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
import plotly.express as px
import plotly.graph_objects as go
# Page config
st.set_page_config(
    page_title='Is it worth it',
    page_icon='😵🙄',
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

st.title("Is it worth it ?")
st.text("Do we clearly see an impact on the pollution levels in the different arrondissement of paris?")
st.text("For exemple there is no closed area in the 15th arrondissement, so is there more pollution there?")
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

# URL de l'API
url = "https://api.airparif.fr/horair/historique"

# Clé d'accès
api_key = "e0553c24-e9e9-c7c4-60bf-207e71a9933f"

# Paramètres de la requête POST
params = {
    "polluants": ["indice", "pm10"],
    "longitude": 2.349792359642986,
    "latitude": 48.827820773320795,
    "datemax": "2023-06-02T02:11:23Z",
    
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

    # Traiter les données comme souhaité
    # Par exemple, afficher les données
    #st.write(data)
#else:
#    # La requête a échoué
#    st.write("La requête a échoué avec le code d'état:", response.status_code)


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

    #else:
    #    # La requête a échoué
    #    st.write(f"La requête a échoué pour la paire de coordonnées ({longitude}, {latitude}) avec le code d'état:", response.status_code)


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

    #else:
    #    # La requête a échoué
    #   st.write(f"La requête a échoué pour la paire de coordonnées ({longitude}, {latitude}) avec le code d'état:", response.status_code)

# Créer un histogramme du degré de pollution par arrondissement
# Calculer la moyenne de l'indice de pollution par arrondissement
mean_indice = df5.groupby('l_ar')['indice'].mean().reset_index()
#fig, ax = plt.subplots()
fig = px.histogram(mean_indice, x="l_ar", y="indice", title="Degré de pollution par arrondissement")

fig.update_traces(marker=dict(color='purple'))


# Trier les arrondissements par ordre de grandeur de l'indice
#sorted_indice = mean_indice.sort_values(ascending=False)

# Tracer l'histogramme avec les arrondissements triés
#sorted_indice.plot(kind='bar', ax=ax)

# Personnaliser le graphique
#ax.set_xlabel('Arrondissement')
#ax.set_ylabel('Indice de pollution')
#ax.set_title('Degré de pollution par arrondissement aujourdhui')
#ax.set_ylim([0, 80])  # Définir l'échelle de l'axe y de 0 à 80
fig.update_traces(hovertemplate="Arrondissement: %{x}<br>Indice: %{y}")

# Afficher le graphique dans Streamlit
#st.pyplot(fig)
st.plotly_chart(fig)

import pandas as pd
import requests
from datetime import datetime, timedelta

# URL de l'API
url = "https://api.airparif.asso.fr/horair/historique"

# Clé d'accès
api_key = "e0553c24-e9e9-c7c4-60bf-207e71a9933f"

# Créer une liste des 20 arrondissements
arrondissements = list(range(1, 21))

# Créer un dictionnaire pour stocker les données d'indice pour chaque arrondissement
data = {f"arrondissement_{arr}": [] for arr in arrondissements}

# Date de début (1er janvier 2022)
start_date = datetime.now()-timedelta(days=6,hours=2)

#date de fin (aujourd'hui)
end_date = datetime.now()

# Parcourir chaque date
current_date = start_date
while current_date <= end_date:
    # Parcourir chaque arrondissement
    for arr in arrondissements:
        # Récupération des coordonnées GPS de l'arrondissement
        gps = df9.loc[df9['c_ar'] == arr, ['longitude', 'latitude']].values.flatten()

        # Paramètres de la requête POST
        params = {
            "polluants": ["indice"],
            "longitude": gps[0],
            "latitude": gps[1],
            "datemax": current_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
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
            data_json = response.json()

            # Récupérer l'indice
            indice = data_json["valeurs"]["indice"][0] if data_json["valeurs"]["indice"] else None

            # Ajouter l'indice à la liste correspondante dans le dictionnaire
            data[f"arrondissement_{arr}"].append(indice)
        #else:
        #    # La requête a échoué
        #    st.write(f"La requête a échoué pour l'arrondissement {arr} et la date {current_date} avec le code d'état:", response.status_code)

    # Passer à la date suivante
    #print('ok')
    current_date += timedelta(days=1)

# Créer le dataframe final df10_histo
df10_histo = pd.DataFrame(data)

# Ajouter la colonne de date
df10_histo["date"] = pd.date_range(start=start_date, end=end_date, freq="D")

# Réarranger les colonnes pour placer la colonne 'date' en premier
df10_histo = df10_histo[['date'] + [col for col in df10_histo.columns if col != 'date']]

#df10_histo.tail(10)
#récupérer le jour de la semaine correspondant à la date dans la colonne date 
df10_histo['jour_semaine'] = df10_histo['date'].dt.day_name()
#df10_histo


def calculer_moyenne_arrondissement(df, arrondissement):
    moyenne = df[arrondissement][1:-1].mean()
    return moyenne

## Titre de l'application
#st.header("Moyenne de pollution par arrondissement")
#
## Liste des arrondissements
#arrondissements = df10_histo.columns[1:-1]
#
#moyennes_par_arrondissement = {}  # Dictionnaire pour stocker les moyennes par arrondissement
## Calculer le nombre de colonnes nécessaires
#nb_colonnes = 20
## Afficher la pollution moyenne par arrondissement sur une semaine
#colonnes = st.columns(nb_colonnes)
## Calcul et affichage de la moyenne de pollution pour chaque arrondissement
#for arrondissement in arrondissements:
#    moyenne = calculer_moyenne_arrondissement(df10_histo, arrondissement)
#    moyennes_par_arrondissement[arrondissement] = moyenne
##reduire la taille des colonnes et de la police
#st.markdown('<style>div[class="element-container stColumn"] > div {padding: 1rem;}</style>', unsafe_allow_html=True)
##st.markdown('<style>div[class="element-container stMetric stMetric-dlzwqecr"] > div {font-size: small;}</style>', unsafe_allow_html=True)
#
#for i, (arrondissement, moyenne) in enumerate(moyennes_par_arrondissement.items()):
#    colonne = colonnes[i]
#    colonne.metric(label=arrondissement, value=str(moyenne))

    #st.metric(label=f"{arrondissement}", value=moyenne)
    #print(f"Arrondissement {arrondissement}: {moyenne}")


# Fonction pour afficher la courbe d'évolution des données
def afficher_courbe_evolution(df, colonne):
    donnees_colonne = df[colonne]
    jours_semaine = df['jour_semaine']
    
    # Créer la figure de la courbe d'évolution avec Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=jours_semaine, y=donnees_colonne, mode='lines', name=colonne,line=dict(color='orange')))
    
    # Personnaliser la mise en forme de la figure
    fig.update_layout(
        title=f"Évolution de {colonne}",
        xaxis_title="Jour de la semaine",
        yaxis_title=colonne,
        hovermode="x",
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    # Afficher la courbe d'évolution avec Streamlit
    st.plotly_chart(fig)   

# Titre de l'application
st.title("Evolution of one arrondissement")

# Sélection de l'arrondissement à afficher
arrondissement = st.selectbox("Arrondissement :", df10_histo.columns[1:21])

# Vérification de l'existence de l'arrondissement
if arrondissement in df10_histo.columns:
    # Affichage de la courbe d'évolution des données
    afficher_courbe_evolution(df10_histo, arrondissement)
else:
    st.write("Veuillez choisir un arrondissement valide.")
