import os
import streamlit as st

def list_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        st.success(f"Fichier '{file_path}' supprimé avec succès!")
    else:
        st.error(f"Le fichier '{file_path}' n'existe pas.")

def main():

    st.set_page_config(
    page_title="Files",
    page_icon="📚",
    layout="wide",)   

    st.title("Gestion des fichiers")
    files_dir = "data"  # Répertoire où sont stockés les fichiers

    files = list_files(files_dir)
    st.subheader("Fichiers disponibles")

    if files:
        for file in files:
            file_path = os.path.join(files_dir, file)
            with st.expander(file):
                st.download_button(
                    label="Télécharger",
                    data=open(file_path, "rb").read(),
                    file_name=file,
                    mime="text/plain"
                )
                if st.button(f"Supprimer", key=file):
                    delete_file(file_path)
                    st.experimental_rerun()
    else:
        st.write("Aucun fichier trouvé.")

if __name__ == "__main__":
    main()
