import streamlit as st
from PIL import Image
# Page config
st.set_page_config(
    page_title='Home page',
    page_icon='🏛',
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
# Titre en grand
st.title("Paris respire, is it efficient ?")

# Load image from file using Pillow
image = Image.open("image_paris_respire.jpeg")
# Display image using Streamlit
st.image(image, caption='Paris Respire Image')
st.write("Paris Respire is a project that aims to reduce the pollution in Paris by reducing the amount of cars in different areas of Paris. The goal of this project is to see if it has a positive impact on air quality.")
st.write("To do so, we will use the data from the website data.gouv.fr and air quality data from Airparif.")
