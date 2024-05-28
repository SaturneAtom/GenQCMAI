# Utiliser l'image-officielle de Python 3.11
FROM python:3.11

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le contenu du répertoire local dans le conteneur
COPY . /app

# Exposer le port utilisé par Streamlit (par défaut: 8501)
EXPOSE 8501

# Commande pour exécuter l'application Streamlit lorsque le conteneur démarre
CMD ["streamlit", "run", "app/app.py"]
