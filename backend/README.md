# Garden Tracker Backend

Django REST API für die Gartenpflanzen-Tracking-App.

## Setup

### 1. Python venv installieren (falls noch nicht vorhanden)

```bash
sudo apt install python3.12-venv
```

### 2. Virtual Environment erstellen und aktivieren

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
# Bearbeite .env nach Bedarf
```

### 5. Datenbank migrieren

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Superuser erstellen (für Admin-Zugang)

```bash
python manage.py createsuperuser
```

### 7. Development Server starten

```bash
python manage.py runserver 0.0.0.0:8000
```

Die API ist dann erreichbar unter:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## API Endpoints

### Pflanzen
- `GET /api/plants/` - Liste aller Pflanzen
- `POST /api/plants/` - Neue Pflanze anlegen
- `GET /api/plants/{id}/` - Pflanzen-Details
- `PUT /api/plants/{id}/` - Pflanze aktualisieren
- `DELETE /api/plants/{id}/` - Pflanze löschen
- `GET /api/plants/{id}/cycles_detail/` - Alle Zyklen einer Pflanze

Query-Parameter:
- `search` - Suche in Name, Sorte, Samenherkunft
- `year` - Filter nach Jahr

### Anbau-Zyklen
- `GET /api/cycles/` - Liste aller Zyklen
- `POST /api/cycles/` - Neuen Zyklus anlegen
- `GET /api/cycles/{id}/` - Zyklus-Details
- `PUT /api/cycles/{id}/` - Zyklus aktualisieren
- `DELETE /api/cycles/{id}/` - Zyklus löschen
- `POST /api/cycles/{id}/add_event/` - Event hinzufügen
- `POST /api/cycles/{id}/add_task/` - Task hinzufügen

Query-Parameter:
- `year` - Filter nach Jahr
- `status` - Filter nach Status
- `plant` - Filter nach Pflanzen-ID

### Events
- `GET /api/events/` - Liste aller Events
- `POST /api/events/` - Neues Event anlegen
- `GET /api/events/{id}/` - Event-Details
- `PUT /api/events/{id}/` - Event aktualisieren
- `DELETE /api/events/{id}/` - Event löschen

Query-Parameter:
- `cycle` - Filter nach Zyklus-ID
- `type` - Filter nach Event-Typ
- `date_from` - Events ab Datum
- `date_to` - Events bis Datum

### Tasks
- `GET /api/tasks/` - Liste aller Tasks
- `POST /api/tasks/` - Neue Task anlegen
- `GET /api/tasks/{id}/` - Task-Details
- `PUT /api/tasks/{id}/` - Task aktualisieren
- `DELETE /api/tasks/{id}/` - Task löschen
- `POST /api/tasks/{id}/toggle_complete/` - Erledigt-Status togglen

Query-Parameter:
- `completed` - Filter nach erledigt (true/false)
- `cycle` - Filter nach Zyklus-ID
- `priority` - Filter nach Priorität (low/medium/high)
- `overdue` - Nur überfällige Tasks (true)

### Dashboard
- `GET /api/dashboard/stats/` - Dashboard-Statistiken

Gibt zurück:
- Gesamtzahl Pflanzen
- Aktuelle Zyklen
- Offene/überfällige Tasks
- Aktuelle Aufgaben
- Ernten der letzten 30 Tage

## MySQL Setup (für Produktion auf Raspberry Pi)

### 1. MySQL/MariaDB installieren

```bash
sudo apt update
sudo apt install mariadb-server python3-dev default-libmysqlclient-dev build-essential
```

### 2. Datenbank und User erstellen

```bash
sudo mysql

CREATE DATABASE garden_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'garden_user'@'localhost' IDENTIFIED BY 'dein-sicheres-passwort';
GRANT ALL PRIVILEGES ON garden_tracker.* TO 'garden_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. .env anpassen

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=garden_tracker
DB_USER=garden_user
DB_PASSWORD=dein-sicheres-passwort
DB_HOST=localhost
DB_PORT=3306
```

### 4. Migrationen ausführen

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Deployment mit Gunicorn

### 1. Gunicorn installieren (schon in requirements.txt)

### 2. Static Files sammeln

```bash
python manage.py collectstatic --noinput
```

### 3. Gunicorn starten

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 4. Systemd Service erstellen (optional)

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

Service aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl start garden-tracker
sudo systemctl enable garden-tracker
sudo systemctl status garden-tracker
```

## Entwicklung

### Neue Migrations erstellen

```bash
python manage.py makemigrations
python manage.py migrate
```

### Shell öffnen

```bash
python manage.py shell
```

### Tests ausführen

```bash
python manage.py test
```
