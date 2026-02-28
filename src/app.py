from flask import Flask, request, jsonify, render_template
from router.db_router import execute
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/store")
def store():
    return render_template("store.html")

@app.route("/api/<module>/<action>", methods=["POST"])
def api(module, action):
    try:
        data = request.json
        if not data:
            data = {}
        result = execute(module, action, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route("/health")
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)