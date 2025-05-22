# 1. Image de base
FROM python:3.12-slim


#
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

# 3) Copier le code et exposer le port
COPY . .
EXPOSE 8000

# 4) Démarrer le serveur FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



