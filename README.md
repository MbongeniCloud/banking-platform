# Banking Platform — Cloud-Native Microservices on AKS

A production-grade, event-driven banking platform built on Azure Kubernetes Service. 
Designed to demonstrate how modern financial systems handle real-time transactions, 
fraud detection, and account management at scale — the same architectural patterns 
used by teams at Capitec, Nedbank, and Standard Bank.

---

## The Problem This Solves

Traditional banking systems are monolithic. When the payments module goes down, 
the entire system goes down. When transaction volume spikes, the whole application 
needs to scale — even parts that are not under load.

This platform was built to solve that. Each concern is isolated into its own service, 
deployable, scalable, and recoverable independently.

---

## Architecture

┌─────────────────┐
                    │   API Gateway   │
                    │   (Ingress)     │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
┌──────────▼──────┐ ┌────────▼───────┐ ┌──────▼──────────┐
│ Account Service │ │  Transaction   │ │ Fraud Detection │
│   FastAPI       │ │   Service      │ │    Service      │
│   Port 8001     │ │   FastAPI      │ │    FastAPI      │
└──────────┬──────┘ │   Port 8002    │ │    Port 8003    │
           │        └────────┬───────┘ └──────▲──────────┘
           │                 │                │
┌──────────▼──────┐          │    ┌───────────┴──────────┐
│   Azure SQL     │          └────►  Azure Service Bus   │
│   Database      │               │  Topic: transactions │
│   (Accounts)    │               │  Sub: fraud-detection│
└─────────────────┘               └──────────────────────┘
                                           │
                          ┌────────────────▼─────────────┐
                          │        Cosmos DB              │
                          │    (Transaction History)      │
                          └───────────────────────────────┘

Observability: Azure Monitor + Application Insights (distributed tracing)
CI/CD: GitHub Actions → Azure Container Registry → AKS rolling deploy
---

## Live Endpoints

The platform is publicly accessible via the API Gateway:

| Service | Health Check | API Docs |
|---|---|---|
| Account Service | http://20.164.86.226/accounts/health | http://20.164.86.226/accounts/docs |
| Transaction Service | http://20.164.86.226/transactions/health | http://20.164.86.226/transactions/docs |
| Fraud Detection | http://20.164.86.226/fraud/health | — |


## Services

### Account Service
Handles the full lifecycle of a bank account — creation, authentication, and 
balance management. Built with FastAPI and backed by Azure SQL Database, which 
provides ACID-compliant transactions critical for financial data integrity.

JWT-based authentication ensures that every request to a protected endpoint is 
verified before any data is touched.

### Transaction Service
Processes deposits, withdrawals, and transfers asynchronously. Every transaction 
is written to Cosmos DB for its horizontal scalability and low-latency reads, then 
published as an event to Azure Service Bus. This decouples the act of recording a 
transaction from everything that needs to react to it.

### Fraud Detection Service
Subscribes to the transactions topic on Azure Service Bus and evaluates every 
incoming transaction against a rule engine in real time. Rules include large 
transaction thresholds, suspiciously round amounts, and high-value withdrawals.

The service is intentionally stateless and rule-based — straightforward to audit, 
extend, and explain to a compliance team.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12 + FastAPI |
| Orchestration | Azure Kubernetes Service (AKS) |
| Messaging | Azure Service Bus (topics and subscriptions) |
| Account Storage | Azure SQL Database |
| Transaction Storage | Azure Cosmos DB |
| Container Registry | Azure Container Registry (ACR) |
| CI/CD | GitHub Actions |
| Observability | Azure Monitor + Application Insights |
| Auth | JWT (python-jose) |
| IaC | Kubernetes manifests + Helm |

---

## Event-Driven Flow

1. A client submits a POST request to the Transaction Service
2. The transaction is written to Cosmos DB with status "pending"
3. The Transaction Service publishes the event to Azure Service Bus
4. The Fraud Detection Service receives the event via subscription
5. Rules are evaluated and a fraud score is generated
6. If flagged, an alert is raised and the transaction status is updated

This entire flow happens asynchronously. The client gets an immediate response 
without waiting for fraud evaluation to complete — the same pattern used in 
production payment systems.

---

## Real-World Scenarios This Handles

**Scenario 1 — A customer transfers R45,000 to an unknown account**
The transaction is recorded and the event is published. The fraud engine detects 
it exceeds the R20,000 withdrawal threshold, scores it, and flags it for review. 
All without blocking the original transaction response.

**Scenario 2 — Transaction volume spikes at month end**
Because the Transaction Service and Fraud Service are separate deployments, only 
the Transaction Service pods need to scale. The fraud engine scales independently 
based on Service Bus queue depth — not transaction volume directly.

**Scenario 3 — The Account Service goes down**
Transactions already in flight continue to be processed. The Service Bus retains 
unprocessed messages until the subscriber recovers. No data is lost.

---

## Project Structure

banking-platform/
├── services/
│   ├── account-service/        # Account lifecycle and JWT auth
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── database.py
│   │   │   ├── telemetry.py
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       └── accounts.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── transaction-service/    # Payment processing and event publishing
│   └── fraud-service/          # Rule-based fraud detection subscriber
├── infra/
│   ├── k8s/                    # Kubernetes manifests
│   └── helm/                   # Helm chart (parameterised for dev/prod)
└── .github/
└── workflows/
└── deploy.yml          # CI/CD pipeline
---

## Deployment

### Prerequisites
- Azure CLI
- kubectl
- Helm 3
- GitHub account with Actions enabled

### Infrastructure provisioned
- AKS cluster: 2 nodes, Standard_D2s_v3
- Azure SQL Database: Basic tier
- Cosmos DB: South Africa North
- Azure Service Bus: Standard tier with topic and subscription
- Azure Container Registry: Basic tier

### CI/CD

Every push to `main` triggers the GitHub Actions pipeline which:
1. Builds Docker images for all three services
2. Pushes images to Azure Container Registry
3. Connects to AKS via service principal
4. Applies Kubernetes manifests
5. Performs a rolling image update with zero downtime

---

## Challenges and How They Were Solved

**ODBC driver installation in CI**
The account service originally used `pyodbc` with the Microsoft MSSQL driver. 
This failed in GitHub Actions because the driver requires system-level installation 
that conflicts with the runner environment. Switched to `pymssql` which uses 
FreeTDS — a lightweight, open-source alternative with no system dependencies.

**ACR Tasks blocked on free tier**
Azure Container Registry Tasks — which allow cloud-side image builds — are not 
available on the Basic SKU without a support request. Resolved by building images 
directly in GitHub Actions runners using Docker, which is the more portable and 
CI-standard approach anyway.

**Service Bus namespace naming constraints**
Azure Service Bus namespace names must be globally unique and cannot end in 
reserved suffixes like `-sb`. Resolved by using a flat, descriptive name without 
hyphens at the end.

**Secret management in Kubernetes**
Secrets are managed via Kubernetes Secret objects applied directly to the cluster. 
The secrets file is excluded from version control via `.gitignore`. Keys are rotated 
after any exposure, enforced by Azure CLI key regeneration commands.

---

## Business Value

This architecture directly addresses concerns that come up in fintech engineering 
interviews and system design rounds:

- **Resilience** — service failures do not cascade. Each service fails independently.
- **Auditability** — every transaction is an immutable event in Cosmos DB.
- **Scalability** — services scale independently based on their own load.
- **Compliance-readiness** — the fraud engine is rule-based and explainable, 
  which matters for FICA and POPIA compliance in South Africa.
- **Observability** — distributed tracing via Application Insights means you can 
  follow a single transaction across all three services in one query.

---

## What I Would Add in Production

- mTLS between services using a service mesh (Linkerd or Istio)
- Horizontal Pod Autoscaler tied to Service Bus queue depth
- Dead letter queue monitoring and alerting
- API rate limiting at the gateway layer
- Integration test suite running in the CI pipeline before deployment
- Azure Key Vault for secret management instead of Kubernetes secrets

---

## Visual Evidence

### All Services Healthy — AKS Pods Running

All six pods across three services are running with zero restarts after 9 days of continuous uptime.

```
NAME                                    READY   STATUS    RESTARTS   AGE
account-service-67dcc567c5-fj94k        1/1     Running   0          9d
account-service-67dcc567c5-fjf9h        1/1     Running   0          9d
fraud-service-586c7948f6-5s5pw          1/1     Running   0          9d
fraud-service-586c7948f6-cb7tt          1/1     Running   0          9d
transaction-service-6cb67979f9-swwq6    1/1     Running   0          9d
transaction-service-6cb67979f9-zhwl9    1/1     Running   0          9d
```

---

### Live Health Endpoints — HTTP 200 OK

All three services respond to health checks through the Nginx ingress gateway at `20.164.86.226`.

**Account Service**
```
GET http://20.164.86.226/accounts/health
StatusCode : 200
Content    : {"status":"healthy","service":"account-service"}
Date       : Fri, 08 May 2026 15:15:34 GMT
```

**Transaction Service**
```
GET http://20.164.86.226/transactions/health
StatusCode : 200
Content    : {"status":"healthy","service":"transaction-service"}
Date       : Fri, 08 May 2026 15:15:37 GMT
```

**Fraud Detection Service**
```
GET http://20.164.86.226/fraud/health
StatusCode : 200
Content    : {"status":"healthy","service":"fraud-service"}
Date       : Fri, 08 May 2026 15:16:36 GMT
```

---

### Distributed Tracing — Azure Application Insights

Application Insights (`banking-insights`, South Africa North) is wired into all three services via OpenCensus. Traces are collected on every HTTP request and shipped to Azure in real time.

**Transaction Search — 51,310 traces recorded**

The search view shows 51.31k traces matching 51.84k spans, logs, and events over a 24-hour window between `2026/05/07 07:50:05` and `2026/05/08 07:50:05`. Each trace captures the request path, duration, call status, and role instance, confirming that all three services are reporting telemetry independently.

**Application Insights Overview**

The overview dashboard confirms:
- Resource group: `rg-banking-platform`
- Location: South Africa North
- Instrumentation Key: `6b702a59-84ec-4717-8bca-424d9a2fd53c`
- Workspace: `managed-banking-insights-ws`
- Failed requests, server response time, server requests, and availability graphs are all active and collecting data.

---

### Alerting — Three Production Alerts Configured

Three metric alerts are active in Azure Monitor targeting the `banking-insights` Application Insights component:

| Alert Name | Condition | Severity | Evaluation Frequency |
|---|---|---|---|
| failed-requests-alert | Failed requests > 5 in 5 minutes | Severity 1 | Every 1 minute |
| high-latency-alert | Avg response time > 2000ms | Severity 2 | Every 1 minute |
| availability-alert | Availability < 100% | Severity 1 | Every 1 minute |

All alerts are enabled and scoped to the production resource group `rg-banking-platform`.

---

### CI/CD Pipeline — GitHub Actions

The build and deploy pipeline runs on every push to `main`. It builds Docker images for all three services, pushes them to Azure Container Registry (`bankingplatformacr`), and applies the Kubernetes deployments to AKS (`banking-aks`).

**Recent pipeline runs (all green):**

| Run | Commit | Branch | Duration | Status |
|---|---|---|---|---|
| #15 | 80deb25 | main | — | Passed |
| #14 | fa68acb | main | 2m 26s | Passed |
| #13 | 436df22 | main | 2m 17s | Passed |
| #12 | cc7b992 | main | 2m 17s | Passed |
| #10 | f71c949 | main | 4m 53s | Passed |

Pipeline: [https://github.com/MbongeniCloud/banking-platform/actions](https://github.com/MbongeniCloud/banking-platform/actions)

---

### Azure Resources — All Provisioned and Active

| Resource | Name | Type | Location |
|---|---|---|---|
| Kubernetes cluster | banking-aks | AKS | South Africa North |
| Container registry | bankingplatformacr | ACR | South Africa North |
| SQL Server | mbongenibanking-sql | Azure SQL | South Africa North |
| Cosmos DB | mbongenibankingcosmos | Cosmos DB | South Africa North |
| Service Bus | mbongenibankingbus | Azure Service Bus | South Africa North |
| Monitoring | banking-insights | Application Insights | South Africa North |
| Resource group | rg-banking-platform | Resource Group | South Africa North |

## Author

Mbongeni — cloud engineer focused on building systems that are 
observable, resilient, and straightforward to reason about.

GitHub: github.com/MbongeniCloud
