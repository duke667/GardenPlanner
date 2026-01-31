# Garden Tracker Frontend

Vue.js 3 Frontend für die Gartenpflanzen-Tracking-App.

## Setup

### 1. Node.js installieren (falls noch nicht vorhanden)

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

### 2. Dependencies installieren

```bash
npm install
```

### 3. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
# Bearbeite .env nach Bedarf
```

### 4. Development Server starten

```bash
npm run dev
```

Die App ist dann erreichbar unter http://localhost:5173

## Features

### Dashboard
- Übersicht aktuelle Anbau-Zyklen
- Offene und überfällige Aufgaben
- Statistiken (Pflanzen, Zyklen, Tasks)
- Ernten der letzten 30 Tage

### Pflanzen-Verwaltung
- Liste aller Pflanzen mit Suche und Filter
- Detailansicht mit vollständigem Lebenszyklus
- Event-Timeline
- Aufgaben-Zuordnung
- Saatgutgewinnung dokumentieren

### Schnelleingabe
- Schnelles Erfassen von Ereignissen
- Kontextsensitive Felder (Ort, Menge)
- Aktuelle Zyklen-Auswahl

### Aufgaben-Verwaltung
- Alle Aufgaben mit Filter
- Überfällig-Anzeige
- Prioritäten
- Pflanzen-Zuordnung

## Responsive Design

Die App ist vollständig responsive und für mobile Geräte optimiert:

- **Mobile**: Bottom-Navigation mit FAB für Schnelleingabe
- **Desktop**: Top-Navigation mit vollständigem Layout
- **Touch-optimiert**: Große Buttons und Tap-Bereiche

## Production Build

### 1. App bauen

```bash
npm run build
```

Die fertigen Dateien landen im `dist/` Verzeichnis.

### 2. Preview

```bash
npm run preview
```

## Deployment auf Raspberry Pi mit Nginx

### 1. Build erstellen

```bash
npm run build
```

### 2. Dateien auf Raspberry Pi kopieren

```bash
# Vom lokalen Rechner
scp -r dist/* pi@raspberry-ip:/var/www/garden-tracker/
```

### 3. Nginx konfigurieren

`/etc/nginx/sites-available/garden-tracker`:

```nginx
server {
    listen 80;
    server_name raspberry-ip;

    # Frontend
    location / {
        root /var/www/garden-tracker;
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

    # Static files
    location /static/ {
        alias /home/sascha/Projects/claude/backend/staticfiles/;
    }
}
```

### 4. Nginx aktivieren

```bash
sudo ln -s /etc/nginx/sites-available/garden-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Entwicklung

### Ordnerstruktur

```
src/
├── components/       # Wiederverwendbare Komponenten
│   ├── PlantCard.vue
│   ├── EventTimeline.vue
│   ├── TaskItem.vue
│   └── StatsWidget.vue
├── views/           # Seiten
│   ├── Dashboard.vue
│   ├── PlantList.vue
│   ├── PlantDetail.vue
│   ├── EventForm.vue
│   └── TaskList.vue
├── router/          # Vue Router
│   └── index.js
├── services/        # API-Client
│   └── api.js
├── App.vue          # Root-Komponente
├── main.js          # Entry Point
└── style.css        # Tailwind CSS
```

### Code-Stil

- Vue 3 Composition API mit `<script setup>`
- Tailwind CSS für Styling
- Axios für API-Calls
- Responsive-First Design

## Troubleshooting

### API-Verbindungsfehler

1. Backend läuft: `http://localhost:8000/api/`
2. CORS richtig konfiguriert im Backend
3. Proxy in `vite.config.js` prüfen

### Build-Fehler

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Nginx 502 Bad Gateway

Backend läuft nicht oder falsche Proxy-Konfiguration:

```bash
# Backend Status prüfen
sudo systemctl status garden-tracker

# Backend neu starten
sudo systemctl restart garden-tracker
```
