import streamlit as st
from PIL import Image
# Titre en grand
st.title("Paris respire, is it efficient ?")

# Load image from file using Pillow
image = Image.open("image_paris_respire.jpeg")
# Display image using Streamlit
st.image(image, caption='Paris Respire Image')
