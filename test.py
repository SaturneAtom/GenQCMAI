from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from langchain_community.callbacks import get_openai_callback

# Load environment variables
load_dotenv()

# Déclaration des variables de session pour stocker les résultats de génération
if 'first_generation_result' not in st.session_state:
    st.session_state.first_generation_result = None
if 'second_generation_result' not in st.session_state:
    st.session_state.second_generation_result = None

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

def main():
    st.title("Chat with your PDF 💬")
    
    pdf = st.file_uploader('Upload your PDF Document', type='pdf', key="pdf_uploader")
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        # Text variable will store the pdf text
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Create the knowledge base object
        knowledgeBase = process_text(text)
        
        st.write("PDF uploaded successfully! 🎉")

        tab1, tab2, tab3 = st.tabs(["Créer une liste de 7 question", "Créer un exercice de texte à trous", "Owl"])

        with tab1:    
            if st.button("Générer", key="list_questions_key"):
                query = "Imaginez-vous être un professeur d'université enseignant un cours basé sur le document fourni. Votre objectif est d'aider les étudiants à mieux comprendre le contenu en formulant des questions pertinentes. Générez une liste de 7 questions qui pourraient être posées aux étudiants pour les guider dans leur apprentissage. Assurez-vous que les questions couvrent les concepts clés, les exemples spécifiques et encouragent une réflexion approfondie sur le sujet"
  
                docs = knowledgeBase.similarity_search(query)

                llm = OpenAI()
                chain = load_qa_chain(llm, chain_type='stuff')
                
                with get_openai_callback() as cost:
                    st.session_state.first_generation_result = chain.run(input_documents=docs, question=query)
                    print(cost)
                
                st.write_stream(st.session_state.first_generation_result)

        with tab2:
            if st.button("Créer un texte à trous (Type 2)", key="text_trou_key"):
                query = "Imaginez-vous être un professeur d'université enseignant un cours basé sur le document fourni. Votre objectif est d'aider les étudiants à mieux comprendre le contenu en formulant des texte à trous pertinentes."
  
                docs = knowledgeBase.similarity_search(query)

                llm = OpenAI()
                chain = load_qa_chain(llm, chain_type='stuff')
                
                with get_openai_callback() as cost:
                    st.session_state.second_generation_result = chain.run(input_documents=docs, question=query)
                    print(cost)
                
                st.write_stream(st.session_state.second_generation_result)
        
    cancel_button = st.button('Cancel')
        
    if cancel_button:
        st.stop()
            
if __name__ == "__main__":
    main()
