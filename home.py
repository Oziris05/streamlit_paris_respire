import streamlit as st

# Titre en grand
st.title("Paris respire, is it efficient ?")

# Sélection de l'image
image_path = "C:\Users\Oswald Benoit\Desktop\PSB\cours\Business_Intelligence\streamlit_Paris_Respire\data\image_paris_respire.jpeg"
image = st.image(image_path, caption="Image de votre choix", use_column_width=True)

# Instructions supplémentaires
st.write("Voici une image de votre choix. Vous pouvez personnaliser le titre et l'image en modifiant les valeurs dans le code.")

# Lien vers votre source de données, etc.
st.write("Source des données : [Lien vers la source des données](https://www.example.com)")
