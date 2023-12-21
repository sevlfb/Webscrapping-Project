import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

df = pd.read_csv('indeed_jobs.csv')
df.drop('Unnamed: 0', axis = 1, inplace =True)
nouvelle_ligne = pd.DataFrame({'Titre':['Test'],'Entreprise':['Test'],'Lieu':['Paris'],'job_id':['Test'],'url_poste':['Test'],'url_company':['Test'],'Compétences':['Test'],'Salaire':['Test'],'Type de poste':['Test'],'Horaires':['Test']})
df = pd.concat([nouvelle_ligne,df], ignore_index=True)
df['Lieu'] = df['Lieu'].replace('Paris (75)', 'Paris')

# Affichage initial du DataFrame
st.write("DataFrame initial :")
st.write(df)

# Options de filtrage pour l'utilisateur
st.sidebar.header('Filtrer le DataFrame')
selected_city = st.sidebar.selectbox('Choisir une ville :', df['Lieu'].unique())
filtered_df = df[df['Lieu'] == selected_city]

# Affichage du DataFrame filtré
st.write(f"DataFrame filtré pour la ville '{selected_city}' :")
st.write(filtered_df)


# Récupération des coordonnées des villes
geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)

# Création des colonnes de latitude et longitude dans le DataFrame
df['LATITUDE'] = None
df['LONGITUDE'] = None

for index, row in df.iterrows():
    location = geolocator.geocode(row['Lieu'])
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

# Ajouter des marqueurs au cluster
for index, row in df.iterrows():
    folium.Marker(
        [row['LATITUDE'], row['LONGITUDE']],
        popup=f"{row['Titre']},{row['Entreprise']},{row['LATITUDE'], row['LONGITUDE']}, {row['Lieu']}",  # Affiche le titre du poste dans le popup
        tooltip='Cliquez pour voir le poste'
    ).add_to(marker_cluster)

# Afficher la carte
folium_static(map)