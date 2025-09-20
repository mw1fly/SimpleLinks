### SimpleLinks

Quick links page generated from a csv file for all those pesky admin panels, or just your favourite sites.

### A work in progress

My goal is to have this run in docker with a self contained webserver or on a regular webserver. 
 - Add functions like add/delete/update/image upload 
 - Add security and admin function.

🔧 Suggested Project Structure

```bash
project-root/
│
├── backend/                     # Future backend code (API, auth, CRUD)
│   ├── app.py                   # Example Flask/FastAPI entrypoint
│   ├── requirements.txt         # Python deps (or package.json if Node.js)
│   └── ...
│
├── frontend/                    # Client-facing static files
│   ├── index.html
│   ├── css/                     # Stylesheets
│   │   └── styles.css
│   ├── js/                      # JavaScript logic
│   │   ├── main.js
│   │   └── tableLoader.js
│   ├── data/                    # Keep your CSVs here
│   │   ├── links.csv
│   │   └── newlinks.csv
│   └── images/                  # All images
│       ├── google-1.jpg
│       ├── youtube-logo.webp
│       └── ...
│
├── docker/                      # Docker-related configs
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf               # Optional if serving via nginx
│
├── .gitignore
├── README.md
└── LICENSE
```

📌 Near-Term Pitfalls

 - CSV handling

Splitting by , will break if you ever have commas inside a field (quotes not handled).

Consider JSON or SQLite later for reliability.

 - File Uploads & Image Management

 - Security

At present it’s just a static page → anyone can see everything.


📌 Basic htaccess added via nginx
 - user and password = admin


📌 Run

```bash
cd SimpleLinks
docker compose up --build



