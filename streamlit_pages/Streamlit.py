import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt

df = pd.read_csv('List_jobs.csv')
df.drop('Unnamed: 0', axis = 1, inplace =True)
# nouvelle_ligne = pd.DataFrame({'Titre':['Test'],'Entreprise':['Test'],'Lieu':['Paris'],'job_id':['Test'],'url_poste':['Test'],'url_company':['Test'],'Compétences':['Test'],'Salaire':['Test'],'Type de poste':['Test'],'Horaires':['Test']})
# df = pd.concat([nouvelle_ligne,df], ignore_index=True)
# df['Lieu'] = df['Lieu'].replace('Paris (75)', 'Paris')

# Supposons que les données sont des chaînes de caractères de forme "{'Ville': '...', 'Région': '...', 'Pays': '...'}"
pattern = "{'Ville': '(.*?)', 'Région': '(.*?)', 'Pays': '(.*?)'}"
df[['Ville', 'Région', 'Pays']] = df['Job Loc'].str.extract(pattern)
df['Ville'] = df['Ville'].apply(lambda x: 'Paris' if x.endswith('Paris') else x)
df['company']= df['company'].str.split(' ·').str[0]
df.drop(columns=['Unnamed: 16', 'Unnamed: 17', 'List of infos from company','Job Loc','Job ID','lightbulb','verified', 'EcoCompany name','Job Tags','CEO'], inplace=True)
# # Affichage initial du DataFrame
# st.write("DataFrame initial :")
# st.write(df)

# Options de filtrage pour l'utilisateur
st.sidebar.header('Filtrer le DataFrame')

# Ajouter l'option supplémentaire à la liste des villes
options_ville = [''] + list(df['Ville'].unique())
# Créer le selectbox pour les villes avec l'option supplémentaire
selected_city = st.sidebar.selectbox('Choisir une ville :', options_ville)

# Ajouter l'option supplémentaire à la liste des noms de sociétés
options_societe = [''] + list(df['Company Name'].unique())
# Créer le selectbox pour les sociétés avec l'option supplémentaire
selected_company = st.sidebar.selectbox('Choisir une société :', options_societe)

# Ajouter l'option supplémentaire au nombre d'employés
options_taillesociete = [''] + list(df['company'].unique())
# Créer le selectbox pour les sociétés avec l'option supplémentaire
selected_taillecompany = st.sidebar.selectbox('Choisir une taille de société :', options_taillesociete)

# Appliquer les filtres combinés
filtered_df = df.copy()

if selected_city != '':
    filtered_df = filtered_df[filtered_df['Ville'] == selected_city]

if selected_company != '':
    filtered_df = filtered_df[filtered_df['Company Name'] == selected_company]

if selected_taillecompany != '':
    filtered_df = filtered_df[filtered_df['company'] == selected_taillecompany]


# Filtrer le DataFrame en conséquence
if selected_company != '':
    filtered_df = df[df['Company Name'] == selected_company]

    # S'il y a des données après le filtrage, afficher la note globale
    if not filtered_df.empty:
        # Obtenir la note globale pour la société sélectionnée
        # Ici, nous supposons que 'Note globale' est une colonne dans votre DataFrame
        note_globale = filtered_df['Note globale'].iloc[0]  # Prendre la première note globale si plusieurs sont présentes
        note_recommandation = filtered_df['''Recommandation de l'entreprise'''].iloc[0]
        note_CEO = filtered_df['CEO Approval'].iloc[0]
        st.write(f"Note globale pour {selected_company} : {note_globale} , avec une recommandation de  {note_recommandation} et une validation du CEO de {note_CEO}")
    else:
        st.write("Cette société n'est pas présente dans le DataFrame.")
else:
    st.write("Pas de score de société à afficher.")

filtered_df.drop(columns=['Note globale','''Recommandation de l'entreprise''', 'CEO Approval'], inplace=True)
# Affichage du DataFrame filtré
st.write(f"Offres : ")
st.write(filtered_df)


# Récupération des coordonnées des villes
geolocator = Nominatim(user_agent="geoapiExercises", timeout=200)

# Création des colonnes de latitude et longitude dans le DataFrame
filtered_df['LATITUDE'] = None
filtered_df['LONGITUDE'] = None

for index, row in filtered_df.iterrows():
    location = geolocator.geocode(row['Ville'])
    if location:
        filtered_df.at[index, 'LATITUDE'] = location.latitude
        filtered_df.at[index, 'LONGITUDE'] = location.longitude

# Suppression des lignes sans coordonnées
filtered_df = filtered_df.dropna(subset=['LATITUDE', 'LONGITUDE'])

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
for index, row in filtered_df.iterrows():
    folium.Marker(
        [row['LATITUDE'], row['LONGITUDE']],
        popup=f"{row['Job Title']},{row['Company Name']}",
        tooltip='Cliquez pour voir le poste',
        icon=folium.Icon(color=choisir_couleur(row['Ecoscore']))  # Utilisez la fonction choisir_couleur
    ).add_to(marker_cluster)

# Afficher la carte
folium_static(map)