# 1. Image de base
FROM python:3.12-slim

# 1) Installer les paquets natifs nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgomp1 \
      ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 2) Copier & installer les dépendances Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copier le code
COPY . .

# 4) Créer un utilisateur non-root
RUN useradd -m myuser
RUN chown -R myuser:myuser /app
USER myuser

# 5) Démarrer le serveur FastAPI
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level debug



