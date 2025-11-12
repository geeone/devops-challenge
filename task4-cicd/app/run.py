from flask import Flask, jsonify
from prometheus_client import (
    Counter, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)

app = Flask(__name__)

# Dedicated Prometheus registry
# to avoid duplicated imports in tests
PROM_REGISTRY = CollectorRegistry()

# Counter base name
REQUEST_COUNT = Counter(
    "health_requests",
    "Total health check requests",
    registry=PROM_REGISTRY,
)

@app.get("/")
def health():
    REQUEST_COUNT.inc()
    return jsonify(ok=True, service="devops-challenge"), 200

@app.get("/metrics")
def metrics():
    return generate_latest(PROM_REGISTRY), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
