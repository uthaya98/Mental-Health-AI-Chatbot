# Kubernetes + Docker Debugging Notes (Interview Prep)

## Scenario
I deployed a Python backend + Spring Cloud Gateway stack to Minikube, with images hosted in GitLab Container Registry. The system initially failed at multiple layers: container startup, registry auth, Kubernetes probes, and runtime resource limits.

## What Broke and How I Fixed It

### 1) Backend container failed with `ModuleNotFoundError: app`
- **Cause:** Docker entrypoint used `python app/main.py`, which ran as a script and broke package imports.
- **Fix:** Switched to module startup via Uvicorn.
- **Final:** `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]`

### 2) Backend crashed when Mongo DNS lookup failed
- **Cause:** Mongo client initialized at import time; bad/unreachable SRV caused app crash.
- **Fix:** Made Mongo initialization lazy and non-fatal; RAG flow now handles DB unavailable cases gracefully.

### 3) GitLab image push/pull failures (`insufficient_scope`, `context canceled`)
- **Cause:** PAT scope/path/auth issues and unstable token exchange.
- **Fix:** Used proper PAT scopes (`read_registry`, `write_registry`), correct image path, and `imagePullSecrets` in K8s.

### 4) Pods in `CrashLoopBackOff`
- **Backend cause:** K8s manifest used wrong port/path (`8000`, `/health`) while app served on `8080`, `/api/health/*`.
- **Gateway cause:** Port mismatch + low memory (`128Mi`) caused `OOMKilled`.
- **Fixes:**
  - Backend probes: `/api/health/live` and `/api/health/ready` on `8080`
  - Gateway container/probe port set to `8083`
  - Gateway `BACKEND_URL` set to `http://chatbot-backend-service:8080`
  - Memory increased to `requests: 256Mi`, `limits: 512Mi`

## Validation Steps
- `kubectl get pods` -> all `1/1 Running`
- `curl /actuator/health` through gateway -> `200 OK`
- Protected `/api/*` endpoints return `401` without token (expected)
- Register/login flow returns JWT; authorized calls succeed with `Bearer <token>`

## Interview Talking Points
- I debugged layer-by-layer: **build -> registry -> scheduling -> probes -> runtime**
- I used `kubectl describe` + pod logs to identify real causes, not assumptions
- I aligned app runtime behavior with K8s manifests (ports, probes, resources)
- I handled resilience by preventing non-critical dependency failures from crashing startup
