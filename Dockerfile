FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pydantic-settings>=2.0.0

# Créer les répertoires de données
RUN mkdir -p data/conversations data/uploads

# Copier le code source
COPY . .

# S'assurer que les fichiers __init__.py existent dans tous les sous-répertoires
RUN find . -type d -not -path "./\.*" -exec touch {}/__init__.py \;

# S'assurer que les répertoires ont les bonnes permissions
RUN chmod -R 755 .

# Exposer le port pour Chainlit
EXPOSE 8000

# Définir les variables d'environnement
ENV PYTHONPATH=/app
ENV CHAINLIT_HOST=0.0.0.0
ENV CHAINLIT_PORT=8000

# Commande pour démarrer l'application
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]