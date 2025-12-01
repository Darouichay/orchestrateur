# Orchestrateur – Installation & Démarrage

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

## Dépendances principales
- FastAPI
- Uvicorn
- React
- Tailwind CSS

---

# 2. Installation du projet

Télécharge le ZIP ou clone le dépôt :

```bash
git clone https://github.com/Darouichay/orchestrateur.git
cd orchestrateur
```

Structure du projet :

```
orchestrateur/
├── backend/
└── frontend/
```

---

# 3. Installation et lancement du Backend (FastAPI)

## Aller dans le dossier backend
```bash
cd backend
```

## Installer les dépendances Python
```bash
pip install -r requirements.txt
```

## Lancer le serveur FastAPI
```bash
uvicorn main:app --reload
```

## Accéder à l’API
- API : http://localhost:8000
- Documentation interactive : http://localhost:8000/docs

---

# 4. Installation et lancement du Frontend (React)

## Aller dans le dossier frontend
```bash
cd frontend
```

## Installer les dépendances JS
```bash
npm install
```

## Lancer le serveur React
```bash
npm start
```

## Accéder à l’interface web
http://localhost:3000/

---

# 5. Configuration de l’API côté front

Le fichier suivant contient l’URL du backend :

```
frontend/src/services/api.js
```

Exemple :
```js
export const API_URL = "http://localhost:8000";
```

Modifie-le si tu utilises un serveur distant ou Docker.

---

# 6. Résumé rapide (cheat-sheet)

## Backend :
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Frontend :
```bash
cd frontend
npm install
npm start
```

---

# 7. Dépendances détaillées (optionnel)

## Backend (FastAPI)
- fastapi
- uvicorn
- pydantic
- requests (si utilisé)

## Frontend (React)
- react
- axios
- tailwindcss
- react-router-dom

---

# Contributions
Fork → modifications → pull request.
Toutes contributions sont les bienvenues.

---

# Licence
Licence à définir (MIT recommandé).
