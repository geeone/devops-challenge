# DevOps Challenge

Implemented a complete DevOps workflow covering **monitoring**, **CI/CD**, and **deployment automation**:  

- **Task 3 – Monitoring:** added a local observability stack with Prometheus + Grafana and integrated application metrics via `/metrics`.  
- **Task 4 – CI/CD:** built a GitHub Actions pipeline to test, build, and validate Dockerized Flask application.  
- **Task 5 – Deployment:** created a minimal Helm chart for WordPress with a basic, self-contained configuration — including image, service, and optional secret management.  

Together, these tasks demonstrate a full lifecycle approach — from monitoring and continuous integration to containerized deployment using modern DevOps practices.

---

## Task 3 — Monitoring Strategy & Implementation

> If you have multiple Ubuntu prod instances, how would you monitor them?  
> What would be your monitoring strategy?

---

### Monitoring Strategy

In a production environment with multiple Ubuntu servers, the goal is to achieve **centralized observability** — collecting system, application, and network metrics in one place with alerting and visualization.

#### Objectives
1. **Visibility:** real-time insight into CPU, memory, disk, and service-level metrics.  
2. **Alerting:** detect anomalies or incidents early (CPU spikes, OOM kills, service downtime).  
3. **Scalability:** single monitoring stack that can scale horizontally as the infrastructure grows.  
4. **Security:** metrics collection with minimal footprint and no exposed internal endpoints.

---

### Architecture Overview

**Tools:**
- **Prometheus** – main metrics collector and time-series database.  
- **Node Exporter** – lightweight agent installed on each Ubuntu host for system metrics.  
- **Grafana** – dashboards and alerting visualization layer.  
- **Alertmanager** – handles alert routing (e-mail, Slack, etc.).  
- **Application metrics** – exposed from apps (Flask, Nginx, etc.) using `/metrics` endpoints.

#### Deployment Strategy
Each Ubuntu instance runs:
- `node_exporter` on port `9100`
- (optional) app-specific exporters, e.g. `blackbox_exporter` or `mysql_exporter`

Prometheus (central server) scrapes:
```yaml
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets:
          - 'prod-node-1:9100'
          - 'prod-node-2:9100'
          - 'prod-node-3:9100'
  - job_name: 'flask-app'
    static_configs:
      - targets:
          - 'prod-node-1:5000'
```

Grafana connects to Prometheus and provides:
- dashboards per instance (CPU, load average, memory usage, network)
- service dashboards (HTTP latency, error rate)
- alert rules (e.g. CPU > 90% for 5 min, memory > 80%, endpoint down)

Alertmanager routes notifications:
- email → devops@company.com  
- Slack → #alerts channel

---

### Implementation (Prototype)

For demonstration, a local monitoring stack was implemented using Docker Compose:

```
task3-monitoring/
├─ docker-compose.yml
└─ prometheus.yml
```

#### Components
- **Flask App (from Task 4)** — exposes `/metrics` endpoint using `prometheus_client`
- **Prometheus** — scrapes metrics from the app container
- **Grafana** — visualizes collected metrics

#### How to Run
```bash
cd task3-monitoring
docker compose up
```

- Prometheus → http://localhost:9090  
- Grafana → http://localhost:3000 (admin/admin)  
- Flask App → http://localhost:5000  
- Metrics → http://localhost:5000/metrics

---

### Suggested Improvements
- Add **Node Exporter** containers to simulate multiple Ubuntu nodes.
- Add **Alertmanager** with Slack/email notifications.
- Create Grafana dashboard JSON for health requests and HTTP latency.
- Secure endpoints with basic auth and TLS (for prod environment).  
- (Optional) Add centralized log aggregation as part of the observability stack.

---

### Summary  
This solution demonstrates a monitoring approach scalable from a single local Flask app to multiple Ubuntu production nodes. It leverages Prometheus + Grafana as the foundation for metrics collection, visualization, and alerting, ensuring visibility and reliability across distributed environments.

---

## Task 4 — CI/CD (GitHub Actions + Docker + PyTest)

### What’s included
- Minimal Flask app with a single health endpoint
- Unit tests via `pytest`
- `Dockerfile` for containerizing the app
- GitHub Actions workflow with **3 jobs**: `build` (Docker) , `test` (PyTest) and `integration` (Health Check)

### Local development
```bash
# 1) Create and activate a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 2) Install dependencies
pip install -r task4-cicd/app/requirements.txt

# 3) Run tests
pytest -q task4-cicd/app/tests

# 4) Run the app locally
python task4-cicd/app/run.py
# open http://127.0.0.1:5000/
```

### Docker (local)
```bash
docker build -t devops-challenge:latest task4-cicd
docker run --rm -p 5000:5000 devops-challenge:latest
# open http://127.0.0.1:5000/
```

### GitHub Actions  
The workflow is located at `.github/workflows/ci.yml`.  
It automatically runs when you:  
- push changes inside `task4-cicd/` or modify the workflow file itself (`.github/workflows/**`);  
- open or update a **pull request** targeting the `main` branch;  
- or trigger it manually via the **“Run workflow”** button in GitHub’s Actions tab.

The pipeline consists of 3 jobs:  
- **build** — builds the Docker image of the app.  
- **test** — installs dependencies and runs PyTest unit tests.  
- **integration** — runs the built container and checks its `/` health endpoint to verify that the service starts correctly.

This ensures every change to the CI/CD task or its configuration is validated automatically.

---

## Task 5 — Helm Chart for WordPress  

This chart provides an **minimal WordPress deployment** intended for technical task demonstration.  
It is designed to pass `helm lint`, render successfully via `--dry-run` or `helm template`, and optionally run on a **local Kubernetes cluster** (for example, Docker Desktop Kubernetes).

---

### Basic validation

```bash
cd task5-helm-wordpress

# 1) Lint chart syntax
helm lint .

# 2) Render manifests without cluster
helm template wp . --debug

# 3) Full dry-run (requires cluster running & kubeconfig set)
helm install wp . --dry-run --debug \
  --set createSecret=false

# 4) Full-dy-run (with secrets enabled)
helm install wp . --dry-run --debug \
  --set createSecret=true \
  --set mysql.password=`<password>`
```

---

### Running with Docker Desktop Kubernetes

If you have Docker Desktop with Kubernetes enabled:

```bash
# Switch context to Docker Desktop
kubectl config use-context docker-desktop

# (Optional) Deploy MySQL using Bitnami chart
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-mysql bitnami/mysql \
	--set auth.database=wordpress \
	--set auth.username=`<user>` \
	--set auth.password=`<password>`

# Deploy WordPress connected to that DB
helm install wp task5-helm-wordpress \
	--set mysql.host=my-mysql.default.svc.cluster.local \
	--set mysql.username=`<user>` \
	--set mysql.password=`<password>` \
	--set createSecret=false

# Port-forward and open in browser
kubectl port-forward svc/wp-wordpress 8080:80
# http://127.0.0.1:8080
```

If you see *“Error establishing a database connection”*, it means MySQL service is not reachable.

---

### Key values
| Key | Description |
|------|-------------|
| `image.repository` / `tag` | WordPress image (default `wordpress:6.8.3-php8.4-apache`) |
| `mysql.host` / `port` / `database` | External MySQL connection parameters |
| `mysql.username` / `mysql.password` | DB credentials (used directly or stored in Secret) |
| `createSecret` | `true` → generate a Secret for credentials; `false` → plain env vars (default false) |
| `service.type` / `port` | Kubernetes Service settings |

> (!) For production deployments, always set `createSecret=true` so credentials are stored securely.

---

### Cleanup

To remove everything:

```bash
helm uninstall wp
helm uninstall my-mysql
```

---

### Suggested Improvements

Features intentionally omitted for simplicity but easily extendable:

- No `persistence` (PVC) — WordPress data is ephemeral.  
- No `ingress` — access via `kubectl port-forward` only.  
- No `_helpers.tpl` — names and labels are inlined for readability.  
- No `existingSecret` support — only one optional Secret created by chart.  
- No resource requests/limits — could be added under `values.yaml → resources`.  
- Add `Ingress` and `persistence` sections for more production-like setup.  
- (Optional) Add a lightweight MySQL subchart for single-command demo.

---

## License

MIT © Architected by [Sergei Denisenko](https://github.com/geeone)
