# Déploiement de l'application

### 1. Modifier le fichier `.env`

Modifier le fichier nommé `.env` dans le dossier /app et ajoutez votre clé API OpenAI :

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Installer les dépendances

Utilisez la commande suivante pour installer les dépendances : 

```plaintext
pip install -r -requirements.txt
```

### 3. Lancer l'application

Utilisez la commande suivante pour lancer l'application avec streamlit:

```plaintext
streamlit run app/Home.py
```

### 4. Accéder à l'application

Ouvrez votre navigateur et accédez à http://localhost:8501 pour voir votre application Streamlit en cours d'exécution.

### Résumé
En suivant ces étapes, vous avez configuré votre application pour utiliser une clé API OpenAI, créé une image Docker, et lancé un conteneur Docker sur le port 8501. Vous pouvez maintenant accéder à votre application Streamlit via votre navigateur.
