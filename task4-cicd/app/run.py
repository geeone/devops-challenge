from flask import Flask, jsonify


app = Flask(__name__)


@app.get("/")
def health():
    return jsonify(ok=True, service="devops-challenge"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
