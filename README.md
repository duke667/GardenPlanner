# 🌱 Garden Tracker - Gartenpflanzen-Tracking-App

Eine vollständige Webanwendung zur Dokumentation des Lebenszyklus von Gartenpflanzen, optimiert für Raspberry Pi und mobile Nutzung.

## Features

- **Pflanzen-Verwaltung**: Stammdaten, Sorten, Samenherkunft
- **Anbau-Zyklen**: Jahresbasierte Dokumentation des Lebenszyklus
- **Ereignisse**: Aussaat, Keimung, Umpflanzen, Gießen, Ernte und mehr
- **Aufgaben**: Manuelle und automatische Task-Verwaltung mit Prioritäten
- **Dashboard**: Übersicht, Statistiken, anstehende Aufgaben
- **Saatgutgewinnung**: Dokumentation von Samen für das nächste Jahr
- **Responsive Design**: Optimiert für Desktop und Mobile

## Technologie-Stack

### Backend
- Python Django 5.x
- Django REST Framework
- MySQL/MariaDB (oder SQLite für Development)
- Gunicorn (Production)

### Frontend
- Vue.js 3 (Composition API)
- Vue Router
- Tailwind CSS
- Axios
- Vite

## Schnellstart

### 1. Voraussetzungen installieren

```bash
# Python venv
sudo apt install python3.12-venv

# Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Backend Setup

```bash
cd backend

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Datenbank
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Server starten
python manage.py runserver 0.0.0.0:8000
```

Backend läuft auf http://localhost:8000
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### 3. Frontend Setup

```bash
cd frontend

# Dependencies
npm install

# Development Server
npm run dev
```

Frontend läuft auf http://localhost:5173

## Deployment auf Raspberry Pi

### 1. MySQL/MariaDB einrichten

```bash
sudo apt update
sudo apt install mariadb-server python3-dev default-libmysqlclient-dev build-essential

sudo mysql
```

```sql
CREATE DATABASE garden_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'garden_user'@'localhost' IDENTIFIED BY 'dein-sicheres-passwort';
GRANT ALL PRIVILEGES ON garden_tracker.* TO 'garden_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Backend `.env` anpassen:
```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=garden_tracker
DB_USER=garden_user
DB_PASSWORD=dein-sicheres-passwort
DB_HOST=localhost
DB_PORT=3306
```

### 2. Backend mit Gunicorn

```bash
cd backend
source venv/bin/activate

# Migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Gunicorn testen
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 3. Systemd Service erstellen

`/etc/systemd/system/garden-tracker.service`:

```ini
[Unit]
Description=Garden Tracker Django App
After=network.target

[Service]
User=sascha
Group=www-data
WorkingDirectory=/home/sascha/Projects/claude/backend
Environment="PATH=/home/sascha/Projects/claude/backend/venv/bin"
ExecStart=/home/sascha/Projects/claude/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind 0.0.0.0:8000 \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start garden-tracker
sudo systemctl enable garden-tracker
sudo systemctl status garden-tracker
```

### 4. Frontend Build

```bash
cd frontend
npm run build
```

### 5. Nginx konfigurieren

```bash
sudo apt install nginx
```

`/etc/nginx/sites-available/garden-tracker`:

```nginx
server {
    listen 80;
    server_name YOUR_RASPBERRY_PI_IP;

    # Frontend
    location / {
        root /home/sascha/Projects/claude/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Backend Admin
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Django Static Files
    location /static/ {
        alias /home/sascha/Projects/claude/backend/staticfiles/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/garden-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Im lokalen Netzwerk zugreifen

Die App ist jetzt erreichbar unter:
- **Haupt-App**: http://RASPBERRY_PI_IP/
- **Admin-Panel**: http://RASPBERRY_PI_IP/admin/

## Projektstruktur

```
garden-tracker/
├── backend/                    # Django Backend
│   ├── config/                 # Django Settings
│   ├── plants/                 # Main App
│   │   ├── models.py           # Datenbank-Models
│   │   ├── serializers.py      # API Serializers
│   │   ├── views.py            # API Views
│   │   └── admin.py            # Admin Config
│   ├── requirements.txt
│   └── manage.py
│
├── frontend/                   # Vue.js Frontend
│   ├── src/
│   │   ├── components/         # Komponenten
│   │   ├── views/              # Seiten
│   │   ├── router/             # Routing
│   │   └── services/           # API Client
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## API-Endpunkte

### Pflanzen
- `GET /api/plants/` - Liste
- `POST /api/plants/` - Erstellen
- `GET /api/plants/{id}/` - Details
- `PUT /api/plants/{id}/` - Update
- `DELETE /api/plants/{id}/` - Löschen

### Anbau-Zyklen
- `GET /api/cycles/` - Liste
- `POST /api/cycles/` - Erstellen
- `GET /api/cycles/{id}/` - Details
- `POST /api/cycles/{id}/add_event/` - Event hinzufügen
- `POST /api/cycles/{id}/add_task/` - Task hinzufügen

### Events
- `GET /api/events/` - Liste
- `POST /api/events/` - Erstellen

### Tasks
- `GET /api/tasks/` - Liste
- `POST /api/tasks/` - Erstellen
- `POST /api/tasks/{id}/toggle_complete/` - Toggle Status

### Dashboard
- `GET /api/dashboard/stats/` - Statistiken

## Verwendung

### 1. Pflanze anlegen
- Navigiere zu "Pflanzen"
- Klicke "+ Neue Pflanze"
- Fülle Name, Sorte und Samenherkunft aus

### 2. Anbau-Zyklus starten
- Öffne eine Pflanze
- System erstellt automatisch Zyklus für aktuelles Jahr
- Oder klicke "Neuen Zyklus anlegen"

### 3. Ereignisse dokumentieren
- In der Pflanzen-Detailansicht: "+ Event"
- Oder Schnelleingabe (Mobile: FAB-Button)
- Wähle Ereignistyp und fülle Details aus

### 4. Aufgaben verwalten
- Navigiere zu "Aufgaben"
- Erstelle manuelle Aufgaben oder verknüpfe mit Pflanzen
- Filtern nach Status (offen/überfällig/erledigt)

### 5. Dashboard nutzen
- Übersicht aktuelle Zyklen
- Anstehende Aufgaben
- Statistiken und Ernten

## Wartung

### Backend neu starten

```bash
sudo systemctl restart garden-tracker
```

### Frontend neu bauen

```bash
cd frontend
npm run build
```

### Logs anzeigen

```bash
# Backend
sudo journalctl -u garden-tracker -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Datenbank-Backup

```bash
mysqldump -u garden_user -p garden_tracker > backup_$(date +%Y%m%d).sql
```

### Datenbank wiederherstellen

```bash
mysql -u garden_user -p garden_tracker < backup_20260130.sql
```

## Troubleshooting

### Backend startet nicht
```bash
sudo systemctl status garden-tracker
sudo journalctl -u garden-tracker -n 50
```

### Frontend zeigt API-Fehler
- Backend läuft: `curl http://localhost:8000/api/`
- CORS-Settings in `backend/config/settings.py` prüfen
- Nginx-Proxy-Config prüfen

### 502 Bad Gateway
- Backend-Service läuft nicht
- Falscher Port in Nginx-Config

## Lizenz

Privates Projekt für den persönlichen Gebrauch.

## Support

Bei Fragen oder Problemen:
1. Logs prüfen
2. README durchlesen
3. Issue erstellen
