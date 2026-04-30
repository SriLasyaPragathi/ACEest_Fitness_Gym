# Phase 7 — CI/CD Architecture Report

This document summarizes the CI/CD architecture, the 14-stage pipeline flow implemented in Phase 6, the deployment strategies we added, and the readiness assessment for production. The tone is human and practical — written as if a colleague is briefing another colleague after a hands-on sprint. Each section is concise and focused on what matters to operate, maintain, and extend the pipeline.

## 1. Overview
This project implements a multi-stage CI/CD pipeline that builds, tests, analyzes, and deploys the `aceest-fitness-api` into a local Minikube cluster. The goal was to provide a realistic, production-like workflow that fits an operator's day-to-day needs: automated checks, quality gates (SonarQube), containerization, and several zero-downtime deployment patterns. Phase 6 delivered 14 discrete stages covering everything from linting and unit tests through advanced deployment strategy testing. This report explains what we built, why it matters, and how to run and validate it locally.

## 2. CI/CD Architecture Overview
The pipeline is implemented in a declarative Jenkinsfile with 14 ordered stages that enforce a build → verify → publish → deploy lifecycle. Key integrations include SonarQube for static analysis, Docker for image builds, Trivy (optional) for container scanning, and Minikube for local Kubernetes deployments. Jenkins acts as the orchestrator and has `kubectl` available in its runtime image to talk to Minikube using a mounted kubeconfig. Artifacts (test results, coverage reports) are archived to allow traceability and post-run analysis.

## 3. Architecture
At a high level the system consists of three moving parts: the CI server (Jenkins), the container engine (Docker), and the runtime platform (Minikube/Kubernetes). Jenkins builds the image, runs tests and quality scans, and then deploys manifests to the `aceest-production` namespace in Minikube. Deployment strategies are implemented as modular k8s manifests and helper scripts under `k8s/` — the Jenkins stage simply invokes those scripts to exercise the strategy. This keeps the pipeline logic in Jenkins minimal and the strategy implementations portable and testable outside Jenkins as well.

## 4. Local Setup and Execution
To reproduce the environment locally: install Docker, Minikube, kubectl, and run Jenkins using `docker-compose-jenkins.yml`. Start Minikube with at least 4 CPUs and 4GB RAM for stable runs and point Docker to the Minikube daemon when building images. Ensure Jenkins has access to a kubeconfig (we mount the host kubeconfig into the Jenkins container in `docker-compose-jenkins.yml`). Follow the Phase 6 execution guide for step-by-step commands and pre-checks.

## 5. Running Tests Manually
Unit and integration tests run via pytest and are executed in Stage 4 and Stage 9 of the pipeline respectively. To run locally: create a Python venv, install `requirements.txt`, and run `pytest tests/ -v` — there are dedicated k8s smoke tests that exercise the deployed services, which require a running Minikube cluster. The smoke tests output JUnit-style XML files so Jenkins can archive results; running them locally produces the same artifacts for debugging and investigation. If tests fail, inspect `tests/` logs, pod logs via `kubectl logs`, and the archived artifacts in Jenkins.

## 6. GitHub Actions Integration
While the current implementation uses Jenkins, adding GitHub Actions is straightforward and useful for repository-level checks. Actions could run the early stages (checkout, lint, unit tests, Sonar scan) and optionally build Docker images that are pushed to a registry for later deployment. Use Actions for PR validation and keep Jenkins for full integration and deployment to Minikube (or production). If desired, I can scaffold a `.github/workflows/ci.yml` that mirrors the first 8 Jenkins stages.

## 7. Jenkins BUILD Integration
Jenkins executes the full 14-stage flow and is configured to respond to Git webhooks for automatic builds. The Jenkins runtime image was extended to include `kubectl` so deployment stages can run directly from the job workspace. The Jenkinsfile captures dynamic versioning for Docker tags, archives artifacts (test results and coverage), and includes safe handling for JUnit artifacts to avoid pipeline failures when files are missing. For production-grade Jenkins, configure credentials for container registries and secure Sonar tokens in Jenkins credentials store.

## 8. SonarQube
SonarQube is integrated as a quality gate in Stage 6; its analysis runs during the pipeline and results appear in the Sonar UI. The local setup uses SonarQube Community edition running on `localhost:9000`; ensure the service is up before running the pipeline. Sonar flags code smells, duplicates, and security hotspots — treat it as an early warning system that blocks merges if thresholds are configured. In time, tune rules to balance noise vs. meaningful coverage for this codebase.

## 9. Docker
Images are built with multiple tags (e.g., `latest`, `v1.0.0`, and a build-specific tag) to support promotion workflows. During Phase 6 we verified image builds inside the Minikube Docker environment to avoid remote registry dependency for local tests. The Dockerfile is kept minimal and layered to speed up iterative builds; scanning is run optionally via Trivy to detect known CVEs. For production, push signed images to a trusted registry and use immutable tags in deployment manifests.

## 10. Minikube
Minikube provides a single-node Kubernetes environment that mirrors production behavior enough for deployment strategy testing. We recommend starting Minikube with `--cpus=4 --memory=4096 --disk-size=20g` to avoid resource pressure during tests. The `aceest-production` namespace contains the deployed resources — after applying manifests verify PV/PVC binding and that pods reach `Running`. Minikube's dashboard and `minikube service <svc> --url` are very handy for manual verification.

## 11. Deployment Strategies Implemented
Phase 6 added modular strategy templates and helper scripts for Blue-Green, Canary, Shadow (traffic mirroring), A/B testing, and Rollback. Each strategy lives under `k8s/<strategy>/` with a `deploy.sh` and small manifest set; they were designed to be invoked independently from the pipeline or locally for manual testing. The Jenkins Stage 14 validates that strategy scripts run and checks for expected outcomes (e.g., new pods ready, traffic split observed). This approach makes it easy to add more strategies or adapt them for a service mesh like Istio later.

## 12. Challenges and Mitigation
We hit a few practical issues while implementing Phase 6: - `APP_VERSION` expansion in declarative Jenkins needed a shell-captured value; fixed by capturing the computed version in the shell step. - Installing `kubectl` via apt inside the Jenkins image failed due to repository issues; we switched to downloading the kubectl binary directly. - A PV/PVC selector mismatch blocked pods; adding labels to the PV fixed Binding. Each problem was fixed at its root, tracked via commits, and validated in the pipeline.

## 13. Key Automation Outcomes
The pipeline now delivers repeatable, observable builds and deployments: automated static analysis, test execution with archived artifacts, container builds, and automated Minikube deployments. Advanced deployment patterns are organized and testable, enabling quick experiments with traffic shifts and rollback drills. The Jenkins image contains `kubectl`, and docker-compose mounts the host kubeconfig so pipeline jobs can interact with Minikube securely. The end result: a local CI/CD environment you can run repeatedly and extend to remote clusters.

## 14. Conclusion
Phase 6 delivered a full end-to-end pipeline and the strategy templates needed to research zero-downtime deployment patterns. Phase 7 (this report) documents what we built, the decisions made, and practical instructions for reproducing and testing the system locally. Next steps are optional: add GitHub Actions for PR-level checks, push images to a remote registry for multi-environment promotion, and add automated strategy-specific end-to-end tests in Jenkins.

---

## Screenshots to Add
- Jenkins pipeline console showing all 14 stages green and Stage 14 strategy validation success.
- `docker-compose-jenkins.yml` showing the kubeconfig mount and Jenkins container running.
- Minikube dashboard filtered to the `aceest-production` namespace (Deployments / Pods / Services view).
- `kubectl get pods -n aceest-production` output with the three `aceest-api` pods in `Running` state.
- `kubectl get pvc,pv -n aceest-production` showing `aceest-pvc` Bound to `aceest-pv`.
- Docker images list showing `aceest-fitness-api:latest`, `v1.0.0`, and the build-specific tag.
- SonarQube project summary page showing the latest analysis and quality gate status.
- A successful `deploy-strategy.sh` console output (for blue-green or canary) showing promotion.

## Suggested Flow Diagrams (what to include)
- Pipeline flow diagram: linear 14-stage flow (Checkout → Build → Lint → Unit Tests → Coverage → Sonar → Docker Build → Scan → Integration → Push → Archive → Deploy → Smoke Tests → Strategy Tests). Annotate which stages run in Jenkins vs. which require external services.
- Deployment strategy diagram: depict two or more clusters/pods and traffic split arrows for Canary / A-B testing, and the Blue ↔ Green swap for Blue-Green.
- Network/credentials diagram: show Jenkins, Minikube, Docker daemon, SonarQube and where credentials and kubeconfig are stored/mounted.

---

If you'd like, I can commit this report to the repository and open a PR, or scaffold a `.github/workflows/ci.yml` that mirrors the first stages of the Jenkins pipeline. Tell me which next step you prefer.
