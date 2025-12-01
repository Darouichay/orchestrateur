# Orchestrateur – Installation et Démarrage

Orchestrateur est une application composée d’un backend FastAPI et d’un frontend React/Tailwind CSS permettant de gérer des hyperviseurs et leurs machines virtuelles.

Ce guide explique toutes les installations nécessaires pour faire fonctionner le projet.

---

# 1. Prérequis

Avant d’installer le projet, assure-toi d’avoir :

## Outils nécessaires
| Outil | Version recommandée | Description |
|-------|---------------------|-------------|
| Python | 3.10+ | Pour exécuter le backend FastAPI |
| pip | dernière version | Gestionnaire de packages Python |
| Node.js | 18+ | Nécessaire pour React |
| npm | 9+ | Gestionnaire de dépendances JS |
| Git | optionnel | Pour cloner et gérer le projet |

## Dépendances Python principales
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- libvirt-python
- python-multipart (obligatoire)

---

# 2. Installation du projet

```bash
git clone https://github.com/Darouichay/orchestrateur.git
cd orchestrateur
```

Structure :

```
orchestrateur/
├── backend/
└── frontend/
```

---

# 3. Installation et lancement du Backend (FastAPI)

## 3.1 Créer un environnement virtuel

```bash
cd backend
python3 -m venv venv
```

Activer l’environnement :

```bash
source venv/bin/activate
```

## 3.2 Installer les dépendances

```bash
pip install -r requirements.txt
pip install python-multipart
```

## 3.3 Lancer le serveur

```bash
uvicorn main:app --reload
```

Accès API :
- http://localhost:8000
- http://localhost:8000/docs

---

# 4. Installation et lancement du Frontend

```bash
cd frontend
npm install
npm start
```

Accès :
http://localhost:3000/

---

# 5. Configuration du frontend

Modifier l’URL de l’API si nécessaire :

```
frontend/src/services/api.js
```

```js
export const API_URL = "http://localhost:8000";
```

---

# 6. Résumé rapide

## Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install python-multipart
uvicorn main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm start
```

---

# 7. Dépendances détaillées

## Backend
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- libvirt-python
- python-multipart

## Frontend
- react
- axios
- tailwindcss
- react-router-dom

---
