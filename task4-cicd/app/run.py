from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST


app = Flask(__name__)

# Prometheus metric: count successful health checks
REQUEST_COUNT = Counter('health_requests_total', 'Total health check requests')


@app.get("/")
def health():
    REQUEST_COUNT.inc()
    return jsonify(ok=True, service="devops-challenge"), 200


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
