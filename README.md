# Système de Gestion de Livraison

## Description du Projet

Un système complet de gestion de livraison et de transport développé avec Django. Cette application permet de gérer les clients, les chauffeurs, les véhicules, les expéditions, les colis, les factures, les tournées et les incidents de livraison.

---

## Technologies Utilisées

### Backend
- **Framework**: Django 6.0
- **Langage**: Python 3.x
- **Serveur Web**: WSGI (avec Django)
- **Base de Données**: SQLite3 (développement)

### Frontend
- **HTML5**: Pour la structure des pages
- **CSS3**: Pour le design et la mise en page (fichiers CSS personnalisés)
- **JavaScript**: Pour l'interactivité côté client
- **Template Engine**: Django Templates

### Authentification et Sécurité
- **Système d'authentification**: Django Auth intégré
- **Hashage des mots de passe**: Django password hashers
- **Protection CSRF**: Middleware CSRF de Django
- **Sécurité**: Middleware de sécurité Django

---

## Frameworks et Bibliothèques Principales

### Backend Django
- **django.contrib.admin**: Interface d'administration Django
- **django.contrib.auth**: Système d'authentification et d'autorisation
- **django.contrib.contenttypes**: Gestion des types de contenu
- **django.contrib.sessions**: Gestion des sessions utilisateur
- **django.contrib.messages**: Système de messages
- **django.contrib.staticfiles**: Gestion des fichiers statiques

### Apps Django du Projet
- **home**: Page d'accueil et interface générale
- **client**: Gestion des clients
- **driver**: Gestion des chauffeurs
- **dashboard**: Tableau de bord administrateur
- **database**: Modèles de données et gestion de la base de données
- **agent**: Gestion des agents

### Middleware
- SecurityMiddleware
- SessionMiddleware
- CommonMiddleware
- CsrfViewMiddleware
- AuthenticationMiddleware
- MessageMiddleware
- XFrameOptionsMiddleware

---

## Architecture du Projet

### Structure des Dossiers

```
backend/
├── config/                      # Fichiers de configuration Django
│   ├── settings.py             # Paramètres du projet
│   ├── urls.py                 # URLs principales
│   ├── wsgi.py                 # Configuration WSGI
│   ├── asgi.py                 # Configuration ASGI
│   ├── views.py                # Vues de configuration
│   └── context_processors.py   # Processeurs de contexte
│
├── database/                    # App de gestion de la base de données
│   ├── models.py               # Modèles ORM (Client, Chauffeur, etc.)
│   ├── admin.py                # Configuration de l'admin
│   └── migrations/             # Migrations de base de données
│
├── home/                        # App page d'accueil
├── client/                      # App gestion des clients
├── driver/                      # App gestion des chauffeurs
├── dashboard/                   # App tableau de bord
├── agent/                       # App gestion des agents
│
├── static/                      # Fichiers statiques
│   ├── css/                    # Fichiers CSS
│   │   ├── dashboard.css
│   │   ├── login.css
│   │   ├── vehicles.css
│   │   ├── invoices.css
│   │   └── ... (autres fichiers CSS)
│   │
│   └── js/                     # Fichiers JavaScript
│       ├── DASHmain.js
│       ├── DASHcharts.js
│       └── ... (autres fichiers JS)
│
├── templates/                   # Fichiers HTML Django
│   ├── base_dashboard.html
│   ├── DASHindex.html
│   ├── DASHshipments.html
│   ├── DASHclients.html
│   ├── login.html
│   ├── loginagent.html
│   ├── loginclient.html
│   ├── logindriver.html
│   └── ... (autres templates)
│
├── manage.py                    # Script de gestion Django
└── db.sqlite3                   # Base de données (développement)
```

---

## Modèles de Données Principaux

Le système gère les entités suivantes:

### 1. **Client**
- Identifiant unique (CL000001, etc.)
- Informations personnelles (nom, prénom, email, téléphone)
- Adresse (adresse, ville, pays)
- Mot de passe chiffré
- Date d'inscription

### 2. **Chauffeur**
- Identifiant unique
- Informations personnelles
- Véhicule assigné
- Statut et disponibilité

### 3. **Véhicule**
- Identifiant unique
- Type de véhicule
- Capacité de charge
- Statut d'entretien

### 4. **Expédition/Livraison (Shipment)**
- Identifiant unique
- Client associé
- Chauffeur assigné
- Date et heure de livraison
- Statut de livraison

### 5. **Colis (Package)**
- Identifiant unique
- Expédition associée
- Description et poids
- Dimensions

### 6. **Facture (Invoice)**
- Identifiant unique
- Client et expédition
- Montant et détails
- Date d'émission

### 7. **Tournée (Tour)**
- Identifiant unique
- Chauffeur assigné
- Liste de livraisons
- Itinéraire

### 8. **Incident/Réclamation**
- Identifiant unique
- Livraison concernée
- Description et statut
- Date du rapport

### 9. **Agent**
- Identifiant unique
- Rôle et permissions
- Informations de connexion

---

## Fonctionnalités Principales

- ✅ Gestion des clients et authentification
- ✅ Gestion des chauffeurs et des véhicules
- ✅ Gestion des expéditions et colis
- ✅ Tableau de bord administrateur
- ✅ Gestion des factures
- ✅ Suivi des tournées
- ✅ Gestion des incidents et réclamations
- ✅ Système de rôles et permissions

---

## Configuration et Installation

### Prérequis
- Python 3.8+
- Django 6.0
- SQLite3

### Installation

```bash
# Cloner le repository
git clone <url-repository>
cd delivery-management-system

# Installer les dépendances
pip install django==6.0

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

---

## Accès à l'Application

- **URL locale**: http://localhost:8000/
- **Admin Django**: http://localhost:8000/admin/
- **Pages d'authentification**:
  - Client: http://localhost:8000/loginclient/
  - Chauffeur: http://localhost:8000/logindriver/
  - Agent: http://localhost:8000/loginagent/

---

## Fichiers de Configuration Importants

- `config/settings.py`: Configuration principale du projet
- `config/urls.py`: Routage des URLs
- `config/wsgi.py`: Configuration WSGI pour déploiement
- `database/models.py`: Définition de tous les modèles de données
- `database/admin.py`: Configuration de l'interface d'administration

---

## Base de Données

- **Type**: SQLite3 (développement)
- **Fichier**: `db.sqlite3`
- **Migrations**: Gérées par Django ORM dans `database/migrations/`

### Migrations disponibles:
- 0001_initial: Création initiale
- 0002-0015: Évolutions et améliorations du schéma

---

## Notes de Développement

- Le projet utilise les bonnes pratiques Django avec une séparation claire entre les applications
- Les mots de passe sont hashés avec les outils de sécurité intégrés de Django
- Les fichiers statiques (CSS, JS) sont organisés par fonctionnalité
- Le système utilise un ORM Django pour les opérations de base de données
- Les templates utilisent le moteur de templates Django avec les processeurs de contexte personnalisés

---

## Version

- **Django**: 6.0
- **Python**: 3.x
- **Date de création**: 2025-2026

---

## Licence

À définir selon vos besoins.

---

*Pour plus d'informations sur Django, consultez la [documentation officielle](https://docs.djangoproject.com/).*
