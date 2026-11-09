AutoHeal Platform 🚑
AutoHeal is a self-healing application platform that automatically detects failures in running containers and recovers them with minimal human intervention. It combines a Flask web application with a Python-based controller that monitors pod health, triggers recovery actions, and exposes metrics for observability.

📋 Table of Contents
Overview

Architecture

Features

Project Structure

Prerequisites

Quick Start

Run with Docker

Run with Docker Compose

Deploy on Kubernetes

Self-Healing Logic

Monitoring & Observability

Testing

CI/CD Pipeline

Configuration

Troubleshooting

Contributing

License

🧭 Overview
AutoHeal demonstrates a complete self-healing loop for containerized applications:

Detect – A failure detector continuously watches pod/container health (readiness, liveness, HTTP probes, logs).

Decide – A self-healing controller evaluates failures against recovery policies.

Recover – A recovery engine restarts, replaces, or reschedules unhealthy pods through the Kubernetes API.

Observe – Prometheus scrapes metrics, and Grafana displays dashboards.

The platform ships with everything you need: application code, Kubernetes manifests, RBAC rules, autoscaling (HPA), monitoring stack, tests, and a CI/CD pipeline.

🏗 Architecture
text
┌──────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                    │
│                                                              │
│   ┌──────────────┐    ┌──────────────────┐                   │
│   │  Flask App   │◄───┤  Failure Detector│                   │
│   │  (Pod(s))    │    └────────┬─────────┘                   │
│   └──────┬───────┘             │                             │
│          │                     ▼                             │
│          │           ┌──────────────────┐                    │
│          │           │ Self-Healing     │                    │
│          │           │ Controller       │                    │
│          │           └────────┬─────────┘                    │
│          │                    ▼                              │
│          │           ┌──────────────────┐                    │
│          └──────────►│ Recovery Engine  │                    │
│                      └────────┬─────────┘                    │
│                               │                              │
│                               ▼                              │
│                    ┌────────────────────┐                    │
│                    │ Kubernetes API     │                    │
│                    └────────────────────┘                    │
│                                                              │
│   ┌────────────┐     ┌────────────┐                          │
│   │ Prometheus │────►│  Grafana   │                          │
│   └────────────┘     └────────────┘                          │
└──────────────────────────────────────────────────────────────┘
✨ Features
🔍 Automated failure detection – Continuous health checks of pods and containers

♻️ Self-healing recovery – Automatic restart/replacement of unhealthy pods

📊 Prometheus metrics – Rich metrics exposed for detection and recovery events

📈 Grafana dashboards – Pre-built JSON dashboards for real-time visibility

☸️ Kubernetes-native – Deployments, Services, HPA, RBAC all included

🔐 Least-privilege RBAC – The controller only has permissions it needs

🐳 Docker & Compose support – Run locally without a cluster

✅ Unit tests – Pytest suite for app and controller logic

🚀 Jenkins pipeline – Full build → test → image → deploy workflow

📁 Project Structure
text
autoheal-platform/
├── app/
│   ├── app.py                  # Flask application
│   ├── requirements.txt
│   └── Dockerfile
├── controller/
│   ├── self_healing_controller.py
│   ├── failure_detector.py
│   ├── recovery_engine.py
│   └── requirements.txt
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── rbac.yaml
│   └── hpa.yaml
├── monitoring/
│   ├── prometheus.yml
│   └── grafana-dashboard.json
├── tests/
│   ├── test_app.py
│   └── test_controller.py
├── docker-compose.yml
├── Jenkinsfile
└── README.md
File names may vary slightly; adjust paths if your project differs.

🧰 Prerequisites
Tool	Version
Python	3.10+
Docker	20.10+
Docker Compose	2.x
Kubernetes (optional)	1.25+
kubectl	matching cluster
Helm (optional)	3.x
🚀 Quick Start
Run with Docker
bash
# Build the image
docker build -t autoheal-app:1.0 ./app

# Run the container
docker run -d --name autoheal-app -p 5000:5000 autoheal-app:1.0

# Verify
curl http://localhost:5000/health
Run with Docker Compose
bash
docker compose up -d --build
This starts:

autoheal-app on port 5000

prometheus on port 9090

grafana on port 3000

Tear down:

bash
docker compose down -v
Deploy on Kubernetes
bash
# 1. Apply RBAC (controller service account + roles)
kubectl apply -f k8s/rbac.yaml

# 2. Deploy the application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 3. Enable autoscaling
kubectl apply -f k8s/hpa.yaml

# 4. Verify
kubectl get pods -l app=autoheal
kubectl get svc autoheal-service
🩺 Self-Healing Logic
The controller runs the following loop every POLL_INTERVAL seconds:

List pods in the target namespace (failure_detector.py).

Classify each pod based on:

Container restarts (restartCount threshold)

Not-Ready condition duration

Failing liveness/readiness probes

CrashLoopBackOff / OOMKilled states

Score the failure and consult the recovery policy (self_healing_controller.py).

Act via the recovery engine (recovery_engine.py):

restart → delete the pod so it's recreated

replace → mark for eviction and let K8s reschedule

escalate → log + emit alert metric

Record the action in Prometheus metrics and structured logs.

Recovery policy example
yaml
# controller/policy.yaml (example)
restart_threshold: 3          # restart after 3 failures
cooldown_seconds: 120         # don't retry within 2 min
max_restarts_per_hour: 5
escalation_webhook: ""        # optional Slack/Teams webhook
📊 Monitoring & Observability
Metrics exposed
Metric	Type	Description
autoheal_pods_monitored_total	Gauge	Pods currently watched
autoheal_failures_detected_total	Counter	Total failures detected
autoheal_recoveries_total	Counter	Recovery actions performed
autoheal_recovery_duration_seconds	Histogram	Time to recover a pod
autoheal_escalations_total	Counter	Failures escalated
Prometheus
Prometheus config lives in monitoring/prometheus.yml. Access UI at:

text
http://localhost:9090
Grafana
Import monitoring/grafana-dashboard.json into Grafana at:

text
http://localhost:3000   (default: admin / admin)
The dashboard shows pod health, detection rate, recovery times, and escalations.

🧪 Testing
bash
# Install dev dependencies
pip install -r app/requirements.txt -r controller/requirements.txt pytest

# Run unit tests
pytest tests/ -v --cov=app --cov=controller --cov-report=term-missing
Tests cover:

Flask endpoint health/readiness

Failure classification logic

Recovery decision rules

Cooldown enforcement

🔁 CI/CD Pipeline
The Jenkinsfile defines a declarative pipeline:

text
Checkout → Install deps → Run tests → Build image
        → Push to registry → Deploy to K8s → Smoke test
Stages run automatically on pushes to main. Pull requests run the test stage only.

To use it:

Create a Jenkins pipeline job pointing at this repository.

Configure credentials: docker-registry-creds, kubeconfig.

Trigger a build.

⚙️ Configuration
Environment variables (app + controller):

Variable	Default	Description
PORT	5000	Flask listen port
LOG_LEVEL	INFO	Logging verbosity
NAMESPACE	default	Namespace to monitor
POLL_INTERVAL	15	Detection loop interval (s)
RESTART_THRESHOLD	3	Failures before restart
COOLDOWN_SECONDS	120	Cooldown between actions
PROMETHEUS_PORT	8000	Metrics endpoint port
🛠 Troubleshooting
Symptom	Likely Cause	Fix
Controller has no permissions	RBAC not applied	kubectl apply -f k8s/rbac.yaml
Metrics endpoint empty	Prometheus can't scrape	Check prometheus.yml target + network policy
Pods repeatedly restart	Recovery loop thrashing	Increase COOLDOWN_SECONDS
Grafana shows no data	Datasource not configured	Add Prometheus datasource manually
HPA not scaling	Metrics server missing	kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
🤝 Contributing
Fork the repository.

Create a feature branch: git checkout -b feature/my-change.

Commit with clear messages.

Run tests locally: pytest tests/.

Open a pull request.

Please ensure all new behavior is covered by unit tests.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

AutoHeal — Because downtime shouldn't need a human on call. 🚑
