# Sugar&Co. — Système de reservation de commande

## Description

Application Django de gestion de commandes.

## Prérequis système (VPS)
- Ubuntu/Debian (ou autre Linux)
- Python 3.13 installé
- pip
- systemd (pour gérer le service)
- Nginx (pour reverse proxy, optionnel mais recommandé)
- SQLite

## Variables d'environnement importantes
Avant de lancer en production, définir :
- SECRET_KEY : clé Django secrète
- DEBUG : false en production
- ALLOWED_HOSTS : noms/ips autorisés (ex: "example.com, 1.2.3.4")
- DATABASE_URL ou variables DB (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

Stocker ces variables dans /etc/environment, systemd Service file ou un fichier .env chargé par votre configuration.

## Mode développement (local)
1. Créer un virtualenv avec Python 3.13 :
    python3.13 -m venv .venv
2. Activer et installer dépendances :
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
3. Configurer les variables d'environnement (ex: DEBUG=True)
4. Lancer les migrations et le serveur :
    make migrate
    make run

Le serveur tourne sur http://127.0.0.1:8000/ par défaut.

## Mode production (VPS)
Étapes générales :
1. Installer Python 3.13 et dépendances système (libpq-dev si Postgres).
2. Créer un virtualenv et installer requirements.txt.
3. Configurer les variables d'environnement (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, DB).
4. Exécuter : make migrate && make collectstatic
5. Démarrer Gunicorn via systemd (exemple de service ci‑dessous).
6. Configurer Nginx pour faire du reverse proxy vers Gunicorn et servir les fichiers statiques.

Points clés :
- DEBUG doit être false.
- Toujours protéger SECRET_KEY.
- Utiliser HTTPS (configurez certbot / letsencrypt sur Nginx).

