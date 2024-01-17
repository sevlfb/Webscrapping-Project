import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

df = pd.read_csv('List_jobs.csv')
df.drop('Unnamed: 0', axis = 1, inplace =True)
# nouvelle_ligne = pd.DataFrame({'Titre':['Test'],'Entreprise':['Test'],'Lieu':['Paris'],'job_id':['Test'],'url_poste':['Test'],'url_company':['Test'],'Compétences':['Test'],'Salaire':['Test'],'Type de poste':['Test'],'Horaires':['Test']})
# df = pd.concat([nouvelle_ligne,df], ignore_index=True)
# df['Lieu'] = df['Lieu'].replace('Paris (75)', 'Paris')

# Supposons que les données sont des chaînes de caractères de forme "{'Ville': '...', 'Région': '...', 'Pays': '...'}"
pattern = "{'Ville': '(.*?)', 'Région': '(.*?)', 'Pays': '(.*?)'}"
df[['Ville', 'Région', 'Pays']] = df['Job Loc'].str.extract(pattern)
df['Ville'] = df['Ville'].apply(lambda x: 'Paris' if x.endswith('Paris') else x)

df.drop(columns=['Unnamed: 16', 'Unnamed: 17', 'List of infos from company','Job Loc','Job ID','lightbulb','verified', 'EcoCompany name','Job Tags','CEO'], inplace=True)
# # Affichage initial du DataFrame
# st.write("DataFrame initial :")
# st.write(df)

# Options de filtrage pour l'utilisateur
st.sidebar.header('Filtrer le DataFrame')

# Ajouter l'option supplémentaire à la liste des villes
options = [''] + list(df['Ville'].unique())
# Créer le selectbox avec l'option supplémentaire
selected_city = st.sidebar.selectbox('Choisir une ville :', options)
# Filtrer le DataFrame en conséquence
filtered_df = df[df['Ville'] == selected_city] if selected_city != '' else df

# Ajouter l'option supplémentaire à la liste des villes
options = [''] + list(df['Company Name'].unique())
# Créer le selectbox avec l'option supplémentaire
selected_company = st.sidebar.selectbox('Choisir une société :', options)
# Filtrer le DataFrame en conséquence
filtered_df = df[df['Company Name'] == selected_company] if selected_company != '' else df



# Affichage du DataFrame filtré
st.write(f"Offres : ")
st.write(filtered_df)


# Récupération des coordonnées des villes
geolocator = Nominatim(user_agent="geoapiExercises", timeout=200)

# Création des colonnes de latitude et longitude dans le DataFrame
df['LATITUDE'] = None
df['LONGITUDE'] = None

for index, row in df.iterrows():
    location = geolocator.geocode(row['Ville'])
    if location:
        df.at[index, 'LATITUDE'] = location.latitude
        df.at[index, 'LONGITUDE'] = location.longitude

# Suppression des lignes sans coordonnées
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])

# Création de la carte
map = folium.Map(location=[48.8566, 2.3522], zoom_start=6)  # Coordonnées de Paris comme exemple

from folium.plugins import MarkerCluster

# Créer un cluster de marqueurs
marker_cluster = MarkerCluster().add_to(map)

def choisir_couleur(valeur):
    if valeur < 1:
        return 'red'
    elif valeur < 2:
        return 'orange'
    else:
        return 'green'


# Ajouter des marqueurs au cluster
for index, row in df.iterrows():
    folium.Marker(
        [row['LATITUDE'], row['LONGITUDE']],
        popup=f"{row['Job Title']},{row['Company Name']},{row['LATITUDE'], row['LONGITUDE']}, {row['Ville']}",
        tooltip='Cliquez pour voir le poste',
        icon=folium.Icon(color=choisir_couleur(row['Ecoscore']))  # Utilisez la fonction choisir_couleur
    ).add_to(marker_cluster)

# Afficher la carte
folium_static(map)