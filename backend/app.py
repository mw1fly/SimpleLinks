from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string
import os
import json

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "devkey")  # needed for sessions

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

#from flask import Flask, request, jsonify, send_from_directory
#import json
#import os
#from werkzeug.utils import secure_filename

# --- Flask App ---
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "devkey123")  # fallback for testing

# --- Config ---
UPLOAD_FOLDER = os.path.join("static", "images")
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg", "gif"}
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "links.json")

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

# --- Upload Route ---
@app.route("/upload", methods=["POST"])
def upload_file():
    print("➡️  /upload POST called")
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
    print("➡️  /links POST called")
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

@app.route("/admin")
def admin_panel():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_from_directory(app.static_folder, "admin.html")

#@app.route("/admin")
#def serve_admin():
#    return send_from_directory(app.static_folder, "admin.html")

@app.route("/images-list")
def images_list():
    folder = os.path.join(app.static_folder, "images")
    files = os.listdir(folder) if os.path.exists(folder) else []
    return jsonify([f"images/{f}" for f in files])

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

# --- Serve Frontend ---
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
