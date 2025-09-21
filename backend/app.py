from flask import Flask, request, jsonify, send_from_directory
import json
import os

from werkzeug.utils import secure_filename
app = Flask(__name__)   # ✅ define app first
UPLOAD_FOLDER = os.path.join("static", "images")
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(save_path)
        return jsonify({"message": "File uploaded", "path": f"images/{filename}"}), 201
    return jsonify({"error": "Invalid file type"}), 400






app = Flask(__name__, static_folder="static", static_url_path="")

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "links.json")


def load_links():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_links(links):
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)


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


# --- Serve Frontend ---
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
