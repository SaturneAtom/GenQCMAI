# Création et Déploiement d'une Application avec Docker

Ce guide explique comment configurer votre application pour utiliser une clé API OpenAI, créer une image Docker et lancer le conteneur Docker sur le port `8501`.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- [Docker](https://www.docker.com/get-started)

## Étapes

### 1. Créer un fichier `.env`

Créez un fichier nommé `.env` à la racine de votre projet et ajoutez votre clé API OpenAI :

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```
# Création et Déploiement d'une Application avec Docker

Ce guide explique comment configurer votre application pour utiliser une clé API OpenAI, créer une image Docker et lancer le conteneur Docker sur le port `8501`.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- [Docker](https://www.docker.com/get-started)

## Étapes

### 1. Créer un fichier `.env`

Modifier le fichier nommé `.env` dans le dossier /app et ajoutez votre clé API OpenAI :

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Construire image Docker 

Utilisez la commande suivante pour lancer le dockerfile situé à la racine du projet : 

```
plaintext
docker build -t <nom_app>
```

### 3. Lancer le conteneur Docker

Utilisez la commande suivante pour lancer un conteneur à partir de l'image Docker que vous venez de créer :

```plaintext
docker run -p 8501:8501 <nom_app>
```

### 4. Accéder à l'application

Ouvrez votre navigateur et accédez à http://localhost:8501 pour voir votre application Streamlit en cours d'exécution.

### Résumé
En suivant ces étapes, vous avez configuré votre application pour utiliser une clé API OpenAI, créé une image Docker, et lancé un conteneur Docker sur le port 8501. Vous pouvez maintenant accéder à votre application Streamlit via votre navigateur.
