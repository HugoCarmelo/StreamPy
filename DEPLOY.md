# Déploiement StreamPy sur Raspberry Pi OS Lite 64-bit

## Prérequis sur le Raspberry Pi

### 1. Mettre à jour le système

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Installer Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

Vérifier :
```bash
docker --version
```

### 3. Installer Docker Compose plugin

```bash
sudo apt install -y docker-compose-plugin
docker compose version
```

### 4. Installer Git et Node.js (pour le build frontend)

```bash
sudo apt install -y git

# Node.js 20 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # doit afficher v20.x
```

---

## Transférer le projet sur le Pi

### Option A — Copie via SCP (depuis votre PC Windows)

Ouvrir PowerShell sur votre PC :

```powershell
scp -r C:\Users\Hugo\Documents\StreamPy\streampy pi@<IP_DU_PI>:~/streampy
```

Remplacez `<IP_DU_PI>` par l'adresse IP de votre Raspberry Pi (ex: `192.168.1.100`).

### Option B — Git (si le projet est sur GitHub/GitLab)

```bash
git clone https://github.com/votre-user/streampy.git ~/streampy
```

---

## Configuration sur le Pi

### 1. Aller dans le dossier du projet

```bash
cd ~/streampy
```

### 2. Créer le fichier .env

```bash
cp .env.example .env
nano .env
```

Remplir les valeurs :
```env
ENCRYPTION_KEY=<une_clé_32_chars_aléatoire>
JWT_SECRET=<un_secret_fort>
ENVIRONMENT=production
```

Générer des clés aléatoires sécurisées :
```bash
# Pour ENCRYPTION_KEY (doit faire exactement 32 bytes en base64)
python3 -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# Pour JWT_SECRET
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Créer le dossier data

```bash
mkdir -p data
```

---

## Build du frontend

Le frontend doit être buildé localement sur le Pi avant de lancer Docker (le docker-compose monte le dossier `dist/` en volume) :

```bash
cd ~/streampy/frontend
npm install
npm run build
cd ..
```

Cela génère le dossier `frontend/dist/`.

---

## Lancer avec Docker Compose

```bash
cd ~/streampy
docker compose up -d
```

Vérifier que tout tourne :
```bash
docker compose ps
docker compose logs -f
```

L'application est accessible sur **http://<IP_DU_PI>**

---

## Démarrage automatique au boot

Docker Compose démarre automatiquement si le service Docker est activé (ce qui est le cas par défaut). Pour vérifier :

```bash
sudo systemctl is-enabled docker
# doit afficher "enabled"
```

Les conteneurs ont `restart: unless-stopped` donc ils redémarreront automatiquement.

---

## Mise à jour du projet

```bash
cd ~/streampy

# Récupérer les nouveaux fichiers (si git)
git pull

# Rebuilder le frontend si des fichiers Vue ont changé
cd frontend && npm install && npm run build && cd ..

# Redémarrer les conteneurs
docker compose down
docker compose up -d --build
```

---

## Commandes utiles

```bash
# Voir les logs du backend
docker compose logs api -f

# Voir les logs nginx
docker compose logs nginx -f

# Arrêter tout
docker compose down

# Redémarrer un service
docker compose restart api

# Accéder au shell du conteneur backend
docker compose exec api sh
```

---

## Trouver l'IP du Raspberry Pi

Sur le Pi :
```bash
hostname -I
```

Ou depuis votre box/routeur, chercher un appareil nommé `raspberrypi`.

---

## Notes

- **Base de données** : SQLite stockée dans `./data/streampy.db` (persistée via volume Docker)
- **Port** : l'application écoute sur le port **80**
- **Architecture ARM64** : toutes les images Docker utilisées (`python:3.12-slim`, `nginx:alpine`, `node:20-alpine`) sont compatibles ARM64/Raspberry Pi 4 & 5
