# EmployManager — Plateforme RH sécurisée

Application web Django de gestion des employés avec authentification JWT, contrôle d'accès par rôles (RBAC), journal d'audit complet et interface moderne en thème jour (Blanc & Bleu corporate).

---

## Aperçu

| Page | Description |
|---|---|
| **Connexion** | Split-screen : formulaire à gauche, illustration décorative à droite |
| **Tableau de bord** | Statistiques, répartition par département, activité récente |
| **Liste des employés** | Recherche, filtres multi-critères, tableau paginé |
| **Fiche employé** | Informations personnelles, professionnelles, salaire (selon rôle) |
| **Journal d'audit** | Toutes les actions tracées avec filtres date/utilisateur/action |
| **Gestion utilisateurs** | Création de comptes, activation/désactivation (ADMIN uniquement) |

---

## Prérequis

- **Docker Desktop** — https://www.docker.com/products/docker-desktop
- **Git** (optionnel)

Aucune installation Python, PostgreSQL ou Node.js requise sur votre machine. Tout tourne dans Docker.

---

## Installation et démarrage

### Étape 1 — Récupérer le projet

```bash
# Décompresser l'archive
unzip employee_manager.zip
cd employee_manager
```

### Étape 2 — Configurer l'environnement

```bash
cp .env.example .env
```

Ouvrez `.env` et modifiez au minimum la `SECRET_KEY` :

```env
SECRET_KEY=votre-cle-secrete-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=employee_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**Générer une SECRET_KEY sécurisée :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
# ou en ligne : https://djecrety.ir
```

### Étape 3 — Lancer les conteneurs

```bash
docker compose up --build
```

Docker va automatiquement :
1. Télécharger les images Python 3.11 et PostgreSQL 15
2. Installer toutes les dépendances Python
3. Attendre que la base de données soit prête
4. Appliquer les migrations
5. Charger les 5 départements initiaux
6. Démarrer le serveur Gunicorn sur le port 8000

> La première fois prend environ 3-5 minutes. Le serveur est prêt quand vous voyez `[INFO] Starting gunicorn`.

### Étape 4 — Créer les migrations (première fois uniquement)

Ouvrez un **deuxième terminal** dans le dossier du projet :

```bash
docker compose exec web python manage.py makemigrations accounts
docker compose exec web python manage.py makemigrations employees
docker compose exec web python manage.py makemigrations audit
docker compose exec web python manage.py migrate
```

### Étape 5 — Créer le compte administrateur

```bash
docker compose exec web python manage.py createsuperuser
```

Exemple :
```
Adresse email : admin@monentreprise.com
Prénom : Admin
Nom : Principal
Password : MotDePasse123!
Password (again) : MotDePasse123!
```

### Étape 6 — Accéder à l'application

| URL | Description |
|---|---|
| http://localhost:8000/accounts/login/ | Application principale |
| http://localhost:8000/admin/ | Interface d'administration Django |
| http://localhost:8000/api/ | API REST (JSON) |

---

## Structure du projet

```
employee_manager/
│
├── config/                         # Configuration centrale Django
│   ├── settings.py                 # Paramètres : JWT, DRF, DB, sécurité, CORS
│   ├── urls.py                     # Routes principales
│   ├── api_urls.py                 # Routes API REST (/api/...)
│   └── wsgi.py                     # Point d'entrée WSGI
│
├── apps/
│   ├── accounts/                   # Gestion des utilisateurs
│   │   ├── models.py               # Modèle User custom (email comme identifiant)
│   │   ├── views.py                # Login, logout, profil, gestion users (templates)
│   │   ├── api_views.py            # JWT obtain / logout (API)
│   │   ├── serializers.py          # Sérialisation User + token JWT custom
│   │   ├── forms.py                # LoginForm, UserCreateForm
│   │   ├── urls.py                 # Routes web accounts/
│   │   ├── admin.py                # Interface admin Django
│   │   └── tests.py                # Tests unitaires authentification
│   │
│   ├── employees/                  # Gestion des employés
│   │   ├── models.py               # Employee, Department
│   │   ├── views.py                # CRUD employés (templates Django)
│   │   ├── dashboard_views.py      # Vue tableau de bord
│   │   ├── api_views.py            # API REST CRUD employés
│   │   ├── serializers.py          # Serializers avec masquage salaire selon rôle
│   │   ├── permissions.py          # IsAdminOrRH, CanViewLogs
│   │   ├── forms.py                # EmployeeForm, EmployeeFilterForm
│   │   ├── urls.py                 # Routes web employees/
│   │   ├── dashboard_urls.py       # Route dashboard/
│   │   ├── admin.py                # Interface admin Django
│   │   ├── tests.py                # Tests vues et permissions
│   │   ├── tests_api.py            # Tests API REST et JWT
│   │   └── management/
│   │       └── commands/
│   │           └── wait_for_db.py  # Commande d'attente PostgreSQL au démarrage
│   │
│   └── audit/                      # Journal d'audit
│       ├── models.py               # AuditLog (action, user, IP, timestamp)
│       ├── middleware.py           # AuditMiddleware (filtre les routes statiques)
│       ├── utils.py                # Fonction log_action() à appeler dans les vues
│       ├── views.py                # Vue liste des logs avec filtres
│       ├── api_views.py            # API REST logs (ADMIN/RH)
│       ├── urls.py                 # Route audit/logs/
│       ├── admin.py                # Interface admin (lecture seule)
│       └── tests.py                # Tests journal d'audit
│
├── templates/                      # Templates Django — thème jour Blanc & Bleu
│   ├── base.html                   # Layout principal : sidebar + topbar + contenu
│   ├── accounts/
│   │   ├── login.html              # Page connexion split-screen avec illustration
│   │   ├── users_list.html         # Liste des utilisateurs (ADMIN)
│   │   └── user_form.html          # Formulaire création utilisateur
│   ├── employees/
│   │   ├── list.html               # Liste avec filtres et recherche
│   │   ├── detail.html             # Fiche employé complète
│   │   ├── form.html               # Formulaire création/modification
│   │   ├── confirm_delete.html     # Confirmation suppression
│   │   └── _info_item.html         # Partial : carte d'information
│   ├── dashboard/
│   │   └── index.html              # Tableau de bord avec statistiques
│   └── audit/
│       └── logs.html               # Journal d'audit avec filtres
│
├── static/                         # Fichiers statiques
│   ├── css/                        # CSS personnalisé (optionnel)
│   ├── js/                         # JS personnalisé (optionnel)
│   └── img/                        # Images et logos
│
├── fixtures/
│   └── initial_data.json           # 5 départements prêts à charger
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline CI/CD GitHub Actions
│
├── Dockerfile                      # Image Docker Python 3.11
├── docker-compose.yml              # Services : web + db (PostgreSQL)
├── requirements.txt                # Dépendances Python
├── manage.py                       # Point d'entrée Django
├── .env.example                    # Modèle de configuration
└── .gitignore                      # Fichiers exclus de Git
```

---

## Rôles et permissions

Trois rôles sont disponibles, configurables lors de la création d'un utilisateur.

| Action | ADMIN | RH | UTILISATEUR |
|---|:---:|:---:|:---:|
| Voir la liste des employés | ✅ | ✅ | ✅ |
| Voir la fiche d'un employé | ✅ | ✅ | ✅ |
| Voir le salaire d'un employé | ✅ | ✅ | ❌ |
| Créer un employé | ✅ | ✅ | ❌ |
| Modifier un employé | ✅ | ✅ | ❌ |
| Supprimer un employé | ✅ | ❌ | ❌ |
| Voir le journal d'audit | ✅ | ✅ | ❌ |
| Gérer les utilisateurs | ✅ | ❌ | ❌ |
| Activer/désactiver un compte | ✅ | ❌ | ❌ |

---

## Données initiales — Départements

5 départements sont fournis dans `fixtures/initial_data.json`. Pour les charger :

```bash
docker compose exec web python manage.py loaddata fixtures/initial_data.json
```

| Code | Département |
|---|---|
| DG | Direction Générale |
| RH | Ressources Humaines |
| IT | Informatique |
| FIN | Finance & Comptabilité |
| COM | Commercial & Marketing |

Pour ajouter vos propres départements :
```bash
docker compose exec web python manage.py shell
```
```python
from apps.employees.models import Department
Department.objects.create(name="Mon Département", code="CODE", description="Description")
exit()
```

---

## Sécurité — Détail des mécanismes

| Mécanisme | Configuration |
|---|---|
| **JWT** | Access token 30 min, Refresh token 7 jours |
| **Blacklist** | Les tokens révoqués sont blacklistés (logout sécurisé) |
| **Rotation** | Chaque refresh génère un nouveau refresh token |
| **RBAC** | Permissions vérifiées dans les vues ET les serializers API |
| **Masquage salaire** | Champ `salary` absent de la réponse API pour les UTILISATEURS |
| **ORM Django** | Zéro requête SQL brute — protection injection SQL native |
| **CSRF** | Middleware Django activé sur tous les formulaires |
| **XSS** | Templates Django auto-échappés + header `X-XSS-Protection` |
| **Clickjacking** | Header `X-Frame-Options: DENY` |
| **Rate limiting** | 20 req/h anonyme, 200 req/h authentifié (DRF Throttling) |
| **Audit** | Chaque action (CRUD, login, logout) loguée avec IP + User-Agent |

---

## API REST — Référence complète

### Authentification

```bash
# Obtenir les tokens
POST /api/auth/token/
Content-Type: application/json

{
  "email": "admin@exemple.com",
  "password": "motdepasse"
}

# Réponse
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 1,
    "email": "admin@exemple.com",
    "full_name": "Admin Principal",
    "role": "ADMIN"
  }
}
```

```bash
# Rafraîchir le token
POST /api/auth/token/refresh/
{ "refresh": "eyJ..." }

# Se déconnecter (blackliste le token)
POST /api/auth/logout/
Authorization: Bearer eyJ...
{ "refresh": "eyJ..." }
```

### Employés

```bash
# Lister les employés
GET /api/employees/
Authorization: Bearer eyJ...

# Filtres disponibles
GET /api/employees/?department=1&status=ACTIF&contract_type=CDI
GET /api/employees/?search=dupont

# Créer un employé (ADMIN/RH)
POST /api/employees/
Authorization: Bearer eyJ...
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@exemple.com",
  "employee_id": "EMP-001",
  "department": 1,
  "position": "Développeur",
  "contract_type": "CDI",
  "status": "ACTIF",
  "hire_date": "2024-01-15",
  "salary": 500000
}

# Voir, modifier, supprimer
GET    /api/employees/1/
PUT    /api/employees/1/
DELETE /api/employees/1/
```

### Journal d'audit

```bash
# Lister les logs (ADMIN/RH uniquement)
GET /api/audit/
Authorization: Bearer eyJ...
```

---

## Interface utilisateur — Design

- **Thème** : Jour — Blanc & Bleu professionnel (corporate)
- **Police** : Inter + Inter Tight (Google Fonts)
- **Icônes** : Heroicons SVG inline (aucune dépendance externe)
- **Couleur principale** : `#1d4ed8` (Bleu)
- **Page de connexion** : Split-screen avec illustration SVG décorative
- **Sidebar** : Navigation fixe avec sections, rôle affiché en bas
- **Responsive** : Adapté mobile (sidebar masquée)

---

## Commandes utiles

```bash
# Démarrer sans rebuild
docker compose up

# Démarrer en arrière-plan
docker compose up -d

# Arrêter
docker compose down

# Arrêter et supprimer la base de données
docker compose down -v

# Voir les logs en temps réel
docker compose logs -f web
docker compose logs -f db

# Ouvrir un terminal dans le conteneur
docker compose exec web bash

# Créer les migrations après modification d'un modèle
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Lancer les tests
docker compose exec web python manage.py test apps/ --verbosity=2

# Collecter les fichiers statiques
docker compose exec web python manage.py collectstatic --noinput

# Charger les données initiales
docker compose exec web python manage.py loaddata fixtures/initial_data.json

# Ouvrir le shell Django
docker compose exec web python manage.py shell
```

---

## Tests

Le projet inclut 25+ tests couvrant :

- Authentification (login valide, login invalide, redirection)
- Permissions par rôle (ADMIN, RH, UTILISATEUR)
- Masquage du salaire selon le rôle
- CRUD employés (création, modification, suppression)
- API REST et tokens JWT
- Journal d'audit (création des entrées, accès restreint)

```bash
# Lancer tous les tests
docker compose exec web python manage.py test apps/ --verbosity=2

# Lancer les tests d'une application
docker compose exec web python manage.py test apps.accounts
docker compose exec web python manage.py test apps.employees
docker compose exec web python manage.py test apps.audit
```

---

## CI/CD — GitHub Actions

Le pipeline `.github/workflows/ci.yml` exécute automatiquement à chaque `push` :

1. **Tests** — Lance tous les tests avec PostgreSQL
2. **Build Docker** — Construit l'image (sur `main` uniquement)
3. **Déploiement** — Template SSH à configurer selon votre infrastructure

Pour activer le déploiement automatique, ajoutez ces secrets dans GitHub :
- `SERVER_HOST` — IP ou domaine du serveur
- `SERVER_USER` — Utilisateur SSH
- `SSH_PRIVATE_KEY` — Clé privée SSH

---

## Résolution des problèmes fréquents

**Port 5432 déjà utilisé :**
```yaml
# Dans docker-compose.yml, changer le port exposé
ports:
  - "5433:5432"
```

**Migrations manquantes :**
```bash
docker compose exec web python manage.py makemigrations accounts employees audit
docker compose exec web python manage.py migrate
```

**Réinitialiser complètement la base de données :**
```bash
docker compose down -v
docker compose up --build
```

**Forcer la mise à jour des templates :**
```bash
docker compose cp templates/. web:/app/templates/
docker compose exec web find /app -name "*.pyc" -delete
docker compose restart web
```

**Vider le cache navigateur :**
`Ctrl + Shift + R` dans le navigateur

---

## Dépendances Python

| Package | Version | Rôle |
|---|---|---|
| Django | 4.2.11 | Framework web principal |
| djangorestframework | 3.15.1 | API REST |
| djangorestframework-simplejwt | 5.3.1 | Authentification JWT |
| psycopg2-binary | 2.9.9 | Connecteur PostgreSQL |
| django-cors-headers | 4.3.1 | Gestion CORS |
| django-environ | 0.11.2 | Variables d'environnement (.env) |
| Pillow | 10.3.0 | Gestion des images (photos employés) |
| django-filter | 24.2 | Filtres API REST |
| whitenoise | 6.6.0 | Serveur de fichiers statiques |
| gunicorn | 21.2.0 | Serveur WSGI de production |