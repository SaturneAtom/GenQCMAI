import streamlit as st

# Configurer le titre de la page et l'icône
st.set_page_config(
    page_title="Exercices AI",
    page_icon="🧠",
)

# En-tête de la page d'accueil avec un titre principal
st.markdown(
    """
    # Création d'exercices à l'aide de l'intelligence artificielle 🤖
    """
)

# Description de l'application
st.write(
    """
    Bienvenue dans notre application de création d'exercices à l'aide de l'intelligence artificielle. 
    Utilisez les différentes fonctionnalités pour générer des questions, des textes à trous 
    ou même des présentations PowerPoint à partir de documents PDF. Sélectionnez une démo dans la barre 
    latérale pour commencer.
    """
)

st.divider()

st.header("Génération avec Pdf")

st.page_link("pages/1_📖_PDF.py", label="Cliquez ici", icon="📖")

st.divider()# 