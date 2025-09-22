from flask import (
    Flask, request, jsonify, send_from_directory,
    session, redirect, url_for, render_template_string, render_template
)
import os
import json
from werkzeug.utils import secure_filename

# --- Flask App ---
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "devkey123")  # fallback for testing
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

# --- Config ---
UPLOAD_FOLDER = os.path.join("static", "images")
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg", "gif"}
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "links.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "data", "config.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# --- Helpers ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def load_links():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    # Default config
    return {"search": {"engine": "google", "url": "https://www.google.com/search?q="}}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

@app.route("/config", methods=["GET"])
def get_config():
    cfg = load_config()
    return jsonify(cfg)

@app.route("/config", methods=["POST"])
def update_config():
    cfg = request.json
    save_config(cfg)
    return jsonify({"status": "success"})


# --- Helpers for search engines ---
def get_engines():
    cfg = load_config()
    return cfg.get("search", {}).get("engines", [])

def add_engine(name, url, logo):
    cfg = load_config()
    if "search" not in cfg:
        cfg["search"] = {}
    if "engines" not in cfg["search"]:
        cfg["search"]["engines"] = []

    # Prevent duplicate names
    for e in cfg["search"]["engines"]:
        if e["name"].lower() == name.lower():
            raise ValueError("Engine already exists")

    cfg["search"]["engines"].append({"name": name, "url": url, "logo": logo})
    save_config(cfg)

def update_engine(name, url=None, logo=None):
    cfg = load_config()
    for e in cfg.get("search", {}).get("engines", []):
        if e["name"].lower() == name.lower():
            if url: e["url"] = url
            if logo: e["logo"] = logo
            save_config(cfg)
            return
    raise ValueError("Engine not found")

def remove_engine(name):
    cfg = load_config()
    engines = cfg.get("search", {}).get("engines", [])
    cfg["search"]["engines"] = [e for e in engines if e["name"].lower() != name.lower()]
    save_config(cfg)


# --- Manage search engines ---
@app.route("/config/engines", methods=["POST"])
def add_update_engine():
    data = request.json
    name = data.get("name")
    url = data.get("url")
    logo = data.get("logo")
    if not all([name, url, logo]):
        return jsonify({"error": "Missing fields"}), 400
    try:
        engines = get_engines()
        # Check if exists
        for e in engines:
            if e["name"].lower() == name.lower():
                e.update({"url": url, "logo": logo})
                save_config(load_config())
                break
        else:
            add_engine(name, url, logo)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/config/engines/<string:name>", methods=["DELETE"])
def delete_engine(name):
    try:
        remove_engine(name)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/config/active", methods=["POST"])
def set_active_engine():
    data = request.json
    engine_name = data.get("engine")
    cfg = load_config()
    engines = cfg.get("search", {}).get("engines", [])

    # Validate selected engine exists
    if not any(e["name"] == engine_name for e in engines):
        return jsonify({"error": "Engine not found"}), 400

    cfg.setdefault("search", {})["engine"] = engine_name
    save_config(cfg)
    return jsonify({"status": "ok"})


# --- Upload Route ---
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        return jsonify({"message": "File uploaded", "path": f"images/{filename}"}), 201
    return jsonify({"error": "Invalid file type"}), 400

# --- API Endpoints ---
@app.route("/links", methods=["GET"])
def get_links():
    return jsonify(load_links())

@app.route("/links", methods=["POST"])
def add_link():
    new_link = request.json
    links = load_links()
    links.append(new_link)
    save_links(links)
    return jsonify({"status": "success", "link": new_link}), 201

@app.route("/links/<int:index>", methods=["DELETE"])
def delete_link(index):
    links = load_links()
    if 0 <= index < len(links):
        removed = links.pop(index)
        save_links(links)
        return jsonify({"status": "deleted", "link": removed})
    return jsonify({"error": "Index out of range"}), 404

@app.route("/links/<int:index>", methods=["PUT"])
def update_link(index):
    links = load_links()
    if 0 <= index < len(links):
        links[index] = request.json
        save_links(links)
        return jsonify({"status": "updated", "link": links[index]})
    return jsonify({"error": "Index out of range"}), 404

@app.route("/links/<int:index>/move", methods=["POST"])
def move_link(index):
    direction = request.json.get("direction")  # "up" or "down"
    links = load_links()
    if 0 <= index < len(links):
        if direction == "up" and index > 0:
            links[index], links[index - 1] = links[index - 1], links[index]
        elif direction == "down" and index < len(links) - 1:
            links[index], links[index + 1] = links[index + 1], links[index]
        else:
            return jsonify({"error": "Cannot move in that direction"}), 400
        save_links(links)
        return jsonify({"status": "success"})
    return jsonify({"error": "Index out of range"}), 404

# --- Image list for picker ---
@app.route("/images-list")
def images_list():
    folder = os.path.join(app.static_folder, "images")
    files = os.listdir(folder) if os.path.exists(folder) else []
    return jsonify([f"images/{f}" for f in files])

# --- Admin Authentication ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin_panel"))
        else:
            return render_template_string("""
                <h2>Login Failed</h2>
                <a href="{{ url_for('login') }}">Try again</a>
            """)
    return render_template_string("""
        <h2>Admin Login</h2>
        <form method="post">
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    """)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin_panel():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_from_directory(app.static_folder, "admin.html")

# --- Frontend ---
@app.route("/")
def home():
    links = load_links()
    config = load_config()
    return render_template("index.html", links=links, config=config)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
