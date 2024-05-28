from dotenv import load_dotenv
from PyPDF2 import PdfReader
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from langchain_community.callbacks import get_openai_callback
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate

st.set_page_config(
    page_title="Mon app",
    page_icon="👋",
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
    # Format the messages here as per your requirement
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

    multiple_choice = PromptTemplate(
    template="List five {subject}.\n{format_instructions}",
    input_variables=["subject"],
    partial_variables={"format_instructions": format_instructions}
    )


    # Get the formatted messages
    format_instructions = get_format_instructions()
    messages = format_messages(query_list_questions, format_instructions)

    # Run the chain and get the response
    with get_openai_callback() as cost:
        chat_response = chain.run(input_documents=docs, question=messages)
        print(cost)
    
     # Parse the response content
    if isinstance(chat_response, str):
        response_content = chat_response
    else:
        response_content = chat_response.content
    
    output_dict = output_parser.parse(response_content)

    return output_dict

def main():
    global result_multiple_choices_generation, result_text_trou_generation, result_one_choice_generation
    
    query_text_trou = "En tant que professeur d'université enseignant un cours basé sur le document fourni, créez 3 exercices à trou pour aider les étudiants à mieux comprendre le contenu. Assurez-vous que chaque exercice présente une phrase tirée du document avec des mots manquants, que les étudiants devront remplir avec des concepts clés, des termes spécifiques ou des exemples pertinents. Format de sortie : une liste de 3 phrases avec des trous à remplir par les étudiants."
    query_multiple_semantic = """Je dispose d'un document PDF qui contient des informations sur [sujet spécifique du document]. Je veux créer des exercices à choix multiple basés sur le contenu de ce document. Voici les étapes et les consignes spécifiques :
    Analyse du document : Identifiez les points clés et les informations importantes dans le document."""
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
        - a) [Option 1]
        - b) [Option 2]
        - c) [Option 3]
        - d) [Option 4]
        
        Réponse correcte : [Indiquez les lettre des réponse correcte]
        Exemple :

        Question : Quelle ville sont française ?
        -
        Options :
        - a) Berlin
        - b) Bordeaux
        - c) Paris
        - d) Rome
        
        - Réponse correcte : b, c

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
        - a) [Option 1]
        - b) [Option 2]
        - c) [Option 3]
        - d) [Option 4]
        
        Réponse correcte : [Indiquez la lettre des réponse correcte]
        Exemple :

        Question : Quelle est la capitale de la France ?
        -
        Options :
        - a) Berlin
        - b) Madrid
        - c) Paris
        - d) Rome
        
        - Réponse correcte : c
    """

    st.header("Création d'exercices avec IA 📚")
    st.subheader("Bienvenue dans l'outil de création d'exercices automatisé à partir de pdf ! 🚀")

   
    pdf = st.file_uploader('Veuillez télécharger un document PDF pour commencer', type='pdf', key="pdf_uploader")
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        knowledgeBase = process_text(text)
        
        st.success('Pdf enregistré!', icon="✅")

        st.divider()

        tab1, tab2, tab3 = st.tabs(["Créer questions à choix multiple", "Créer un exercice de texte à trous", "Créer questions à choix unique"])    
       
        with tab1:    
            if st.button("Générer liste de questions", key="list_questions_key"):
                if result_multiple_choices_generation is None:
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
                        print(cost)
                st.write(result_multiple_choices_generation)

        with tab2:
            if st.button("Générer texte à trous", key="text_trou_key"):
                if result_text_trou_generation is None:
                    docs = knowledgeBase.similarity_search(query_multiple_semantic)
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
                        print(cost)
                st.write(result_text_trou_generation)

        with tab3:
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
                        print(cost)
                print(result_one_choice_generation)
                st.write(result_one_choice_generation)
           
if __name__ == "__main__":
    main()

