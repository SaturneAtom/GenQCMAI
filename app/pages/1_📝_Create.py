from dotenv import load_dotenv
from PyPDF2 import PdfReader
import streamlit as st
import re
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from langchain_community.callbacks import get_openai_callback
from langchain.output_parsers import CommaSeparatedListOutputParser
import os

st.set_page_config(
    page_title="Create",
    page_icon="📝",
    layout="wide",
)
# Load environment variables
load_dotenv()

# Déclaration des variables globales pour stocker les résultats de génération
result_multiple_choices_generation = None
result_one_choice_generation = None
result_text_trou_generation = None

output_parser = CommaSeparatedListOutputParser()

# Define the function JSON for quiz generation

def process_text(text):
    # Split the text into chunks using Langchain's CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=300,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Convert the chunks of text into embeddings to form a knowledge base
    embeddings = OpenAIEmbeddings()
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    
    return knowledgeBase

def get_format_instructions():
    return output_parser.get_format_instructions()

def format_messages(text, format_instructions):
    return f"{text}\n\n{format_instructions}"

def run_chain(docs, query_list_questions):
    # Initialise LLM
    llm = OpenAI(
        model="gpt-3.5-turbo-instruct",
        temperature=0.5,
        max_tokens=250,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0
    )

    # Initialise QA Chain
    chain = load_qa_chain(llm)

    # Get the formatted messages
    format_instructions = get_format_instructions()
    messages = format_messages(query_list_questions, format_instructions)

    # Run the chain and get the response
    with get_openai_callback() as cost:
        chat_response = chain.run(input_documents=docs, question=messages)
        print(cost)
    
    response_content = chat_response if isinstance(chat_response, str) else chat_response.content
    output_dict = output_parser.parse(response_content)
    return output_dict

def format_for_export(questions):
    formatted_questions = ""
    for question in questions.split("\n\n"):
        if question.strip():
            formatted_question = question.replace("-", "").replace("Options :", "").replace("Options:", "").replace("Question 1: ", "Question: ").replace("Question 2: ", "Question: ").strip()
            formatted_questions += f"{formatted_question}\n\n"
    return formatted_questions

def clean_filename(filename):
    # Replace spaces with underscores and remove special characters
    cleaned_name = re.sub(r'[^A-Za-z0-9_]+', '', filename.replace(" ", "_"))
    return cleaned_name

def write_to_file(file_path, content):
    with open(file_path, 'a') as file:
        file.write(content + "\n\n")

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        st.success(f"Fichier supprimé avec succès!")
    else:
        st.error(f"Le fichier n'existe pas.")


def main():
    global result_multiple_choices_generation, result_text_trou_generation, result_one_choice_generation, multiple_choice_file
    query_multiple_semantic = """
    Je dispose d'un document PDF qui contient des informations sur [sujet spécifique du document]. Je veux créer des exercices à choix multiple basés sur le contenu de ce document. Voici les étapes et les consignes spécifiques :
    Analyse du document : Identifiez les points clés et les informations importantes dans le document."""
    
    query_text_a_trou_semantic = """
    Je dispose d'un document PDF qui contient des informations sur [sujet spécifique du document]. Je veux créer des exercices à trous basés sur le contenu de ce document. Voici les étapes et les consignes spécifiques :
    Analyse du document : Identifiez les points clés et les informations importantes dans le document.
    """
    
    query_text_trou = """
    Création de texte à trous : Formulez 2 exercices de texte à trous pour aider les étudiants à mieux comprendre le contenu. Assurez-vous que chaque exercice présente une phrase tirée du document avec des mots manquants, que les étudiants devront remplir avec des concepts clés, des termes spécifiques ou des exemples pertinents. 
    Options de réponse :
    Important : Assurez-vous que chaque exercice a un ou plusieurs mots manquants, et que les options de réponse sont pertinentes et correctes.
    Utilisez le format suivant pour chaque question :
    
    Exemple:
    - La ____ est l'unité de base de la matière. 
    
    - Options: 
        - A: Molécule
        - B: Atome
        - C: Élément
    
    - Réponse correcte: A

    Exemple :
    - La ____ est une force qui attire les objets vers le centre de la terre.
    
    - Options: 
        - A: Gravitation
        - B: Électricité
        - C: Magnétisme
    
    - Réponse correcte: A
    """


    
    query_multiple_choice = """
    Création des questions : Formulez 2 questions claires et précises basées sur ces points clés. Chaque question doit être conçue pour tester la compréhension des informations importantes contenues dans le document.
    Options de réponse :
    Fournissez quatre options de réponse pour chaque question.
    Important : Assurez-vous que chaque question à plusieurs réponse (au moins deux réponses correctes)
    Les options incorrectes (distracteurs) doivent être plausibles mais incorrectes.
    Format :
    Utilisez le format suivant pour chaque question :
    Question : [Insérez la question ici]
    -
    Options :
    - A: [Option 1]
    - B: [Option 2]
    - C: [Option 3]
    - D: [Option 4]
    
    Réponse correcte : [Indiquez les lettre des réponse correcte]
    Exemple :
    Question : Quelle ville sont française ?
    -
    Options :
    - A: Berlin
    - B: Bordeaux
    - C: Paris
    - D: Rome
    
    - Réponse correcte : B, C
    """
    
    query_one_choice = """
    Création des questions : Formulez 2 questions claires et précises basées sur ces points clés. Chaque question doit être conçue pour tester la compréhension des informations importantes contenues dans le document.
    Options de réponse :
    Fournissez quatre options de réponse pour chaque question.
    Important : Assurez-vous que chaque question a une seule bonne réponse.
    Les options incorrectes (distracteurs) doivent être plausibles mais incorrectes.
    Format :
    Utilisez le format suivant pour chaque question :
    Question : [Insérez la question ici]
    -
    Options :
    - A: [Option 1]
    - B: [Option 2]
    - C: [Option 3]
    - D: [Option 4]
    
    Réponse correcte : [Indiquez la lettre des réponse correcte]
    Exemple :
    Question : Quelle est la capitale de la France ?
    -
    Options :
    - A: Berlin
    - B: Madrid
    - C: Paris
    - D: Rome
    
    - Réponse correcte : C
    """

    st.header("Création d'exercices avec IA 📚")
    st.subheader("Bienvenue dans l'outil de création d'exercices automatisé à partir de pdf ! 🚀")
   
    pdf = st.file_uploader('Veuillez télécharger un document PDF pour commencer', type='pdf', key="pdf_uploader")
    
    if pdf is not None:
        pdf_name = clean_filename(pdf.name.split(".")[0])  # Nettoyer le nom du fichier
        

        #one_choice_file = f"questions_choix_unique_{pdf_name}.txt"
        
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        knowledgeBase = process_text(text)
        
        st.success('Pdf enregistré!', icon="✅")

        st.divider()

        tab1, tab2, tab3 = st.tabs(["Créer questions à choix multiple", "Créer un exercice de texte à trous", "Créer questions à choix unique"])    
       
        with tab1:
            multiple_choice_file = f"data/questions_choix_multiple_{pdf_name}.txt"
            st.success("Projet de questions à choix multiples initialisé!")
            st.divider()
            if st.button("Générer liste de questions", key="list_questions_key"):
                    docs = knowledgeBase.similarity_search(query_multiple_semantic)
                    llm = OpenAI(
                        model="gpt-3.5-turbo-instruct",
                        temperature=0.5,
                        max_tokens=1000,
                        top_p=1.0,
                        frequency_penalty=0.5,
                        presence_penalty=0.0
                    )
                    chain = load_qa_chain(llm)
                    with get_openai_callback() as cost:
                        result_multiple_choices_generation = chain.run(input_documents=docs, question=query_multiple_choice)
                        st.write(cost)
                        st.write(result_multiple_choices_generation)
                        st.divider()
                    write_to_file(multiple_choice_file, format_for_export(result_multiple_choices_generation))


                    
            if os.path.exists(multiple_choice_file):
                with open(multiple_choice_file, "r") as file:
                    file_content_qcm = file.read()
                    st.text_area("Résultats actuels", value=file_content_qcm, height=600, key="multiple_choice_area")
                    st.download_button(
                        label="Télécharger les questions à choix multiple",
                        data=file_content_qcm,
                        file_name=multiple_choice_file,
                        mime="text/plain"
                    )
            if st.button("Supprimer fichier", key="delete_texte-trou_file"):
                delete_file(multiple_choice_file)
                st.rerun()
        with tab2:
            text_trou_file = f"data/questions_texte_trou_{pdf_name}.txt"
            st.success("Projet de questions à texte à trous initialisé!")
            st.divider()
            if st.button("Générer texte à trous", key="text_trou_key"):
                docs = knowledgeBase.similarity_search(query_text_a_trou_semantic)
                llm = OpenAI(
                    model="gpt-3.5-turbo-instruct",
                    temperature=0.5,
                    max_tokens=250,
                    top_p=1.0,
                    frequency_penalty=0.5,
                    presence_penalty=0.0
                )
                chain = load_qa_chain(llm, chain_type="stuff")
                with get_openai_callback() as cost:
                    result_text_trou_generation = chain.run(input_documents=docs, question=query_text_trou)
                    st.write(cost)
                    st.write(result_text_trou_generation)
                    write_to_file(text_trou_file, format_for_export(result_text_trou_generation))
            
            if os.path.exists(text_trou_file):
                with open(text_trou_file, "r") as file:
                    file_content_text_trou = file.read()
                    st.text_area("Résultats actuels", value=file_content_text_trou, height=600, key="text_trou_area")
                    st.download_button(
                    label="Télécharger les questions texte à trous",
                    data=open(text_trou_file, "r").read(),
                    file_name=text_trou_file,
                    mime="text/plain"
                )
            if st.button("Supprimer fichier", key="delete_text_trou_file"):
                delete_file(text_trou_file)
                st.rerun()
            st.divider()

        with tab3:
            one_choice_file = f"data/questions_choix_unique_{pdf_name}.txt"
            st.success("Projet de questions à choix unique initialisé!")
            st.divider()
            if st.button("Générer question à choix unique", key="one_choice_key"):
                if result_one_choice_generation is None:
                    docs = knowledgeBase.similarity_search(query_multiple_semantic)
                    llm = OpenAI(
                        model="gpt-3.5-turbo-instruct",
                        temperature=0.5,
                        max_tokens=250,
                        top_p=1.0,
                        frequency_penalty=0.5,
                        presence_penalty=0.0
                    )
                    chain = load_qa_chain(llm, chain_type='stuff')
                    with get_openai_callback() as cost:
                        result_one_choice_generation = chain.run(input_documents=docs, question=query_one_choice)
                        st.write(cost)
                        st.write(result_one_choice_generation)
                        write_to_file(one_choice_file, format_for_export(result_one_choice_generation))
                    
            if os.path.exists(one_choice_file):
                with open(one_choice_file, "r") as file:
                    file_content_one_choice = file.read()
                    st.text_area("Résultats actuels", value=file_content_one_choice, height=600, key="one_choice_area")
                    st.download_button(
                        label="Télécharger les questions à choix unique",
                        data=open(one_choice_file, "r").read(),
                        file_name=one_choice_file,
                        mime="text/plain"
                )
            if st.button("Supprimer fichier", key="delete_one_choice_file"):
                delete_file(one_choice_file)
                st.rerun()
                
                    
if __name__ == "__main__":
    main()

