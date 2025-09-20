from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "links.json")


def load_links():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_links(links):
    with open(DATA_FILE, "w") as f:
        json.dump(links, f, indent=2)


@app.route("/links", methods=["GET"])
def get_links():
    """Return all links"""
    return jsonify(load_links())


@app.route("/links", methods=["POST"])
def add_link():
    """Add a new link"""
    new_link = request.json
    links = load_links()
    links.append(new_link)
    save_links(links)
    return jsonify({"status": "success", "link": new_link}), 201


@app.route("/links/<int:index>", methods=["DELETE"])
def delete_link(index):
    """Delete a link by index"""
    links = load_links()
    if 0 <= index < len(links):
        removed = links.pop(index)
        save_links(links)
        return jsonify({"status": "deleted", "link": removed})
    return jsonify({"error": "Index out of range"}), 404


@app.route("/links/<int:index>", methods=["PUT"])
def update_link(index):
    """Update a link by index"""
    links = load_links()
    if 0 <= index < len(links):
        links[index] = request.json
        save_links(links)
        return jsonify({"status": "updated", "link": links[index]})
    return jsonify({"error": "Index out of range"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
