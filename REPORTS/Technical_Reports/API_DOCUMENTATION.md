# NOVANEST — REST API SPECIFICATION
## Comprehensive Endpoints Reference, Request/Response Schemas, RBAC & Error Contracts

**Document Version:** 2.0.0 (Production Commissioned)  
**Base URL:** `http://localhost:8001` (Direct API) or `https://novanest.app/api` (via Nginx Reverse Proxy)  
**OpenAPI Specification:** Available interactively at `/docs` (Swagger UI) and `/redoc` (ReDoc)  

---

### 1. Authentication & Role-Based Access Control (RBAC)

All endpoints (except unauthenticated health probes) enforce token authentication passed via the `Authorization: Bearer <token>` or `X-API-Key: <token>` HTTP headers.

#### RBAC Scopes Matrix

| Role | Environment Key | Allowed Scopes | Description & Permissions |
| :--- | :--- | :--- | :--- |
| **`viewer`** | `NOVANEST_VIEWER_KEY` | `read` | Read-only access to business metrics, Customer 360, Restaurant 360, Rider operations, ML predictions, and prescriptive recommendations. Mutation endpoints return **HTTP 403 Forbidden**. |
| **`operator`** | `NOVANEST_API_KEY` | `read`, `operator` | Operational control: approve prescriptive recommendations, initiate execution, record realized outcomes, execute simulations, and interact with conversational AI agents. |
| **`admin`** | `NOVANEST_ADMIN_KEY` | `read`, `operator`, `admin` | Full administrative control: secret key rotation, automated backup triggering, isolated disaster recovery drills, and system re-indexing. |

#### Single-Use Streaming Ticket Exchange Protocol
To prevent leaking static API tokens in URL query strings during Server-Sent Events (SSE) connections, clients must exchange their token for a short-lived ticket:
1. Client calls `POST /api/ai/stream-ticket` with standard `Authorization: Bearer <token>` header.
2. Server validates token, derives caller `AuthPrincipal`, and issues a single-use ticket string (`st_<urlsafe_token>`) valid for 60 seconds.
3. Client establishes `EventSource` connection at `GET /api/ai/ask/stream?ticket=st_...`.
4. Server atomically consumes and invalidates the ticket upon connection establishment, preventing replay attacks.
5. Any direct request passing static tokens in query parameters (`?token=...`) is strictly rejected with **HTTP 401 Unauthorized**.

---

### 2. Standard Error Response Contract

All error responses adhere to a consistent JSON structure:

```json
{
  "detail": "Descriptive human-readable explanation of the error condition.",
  "error_code": "RESOURCE_NOT_FOUND",
  "request_id": "req_01h7x8...",
  "timestamp": "2026-11-15T09:20:00Z"
}
```

| HTTP Status | Meaning | Typical Trigger |
| :---: | :--- | :--- |
| **`200 OK`** | Request succeeded. | Standard successful query or operation. |
| **`400 Bad Request`** | Invalid input payload or state transition. | Attempting to approve a recommendation that is not in `PROPOSED` state. |
| **`401 Unauthorized`** | Missing, invalid, or expired authentication token. | Calling protected route without `Authorization` header. |
| **`403 Forbidden`** | Authenticated user lacks required RBAC scope. | `viewer` role attempting to call `/approve` (requires `operator`). |
| **`404 Not Found`** | Requested entity does not exist. | Querying invalid customer ID `/api/customer/360/C999999`. |
| **`429 Too Many Requests`** | Rate limit threshold exceeded. | Client exceeding 50 requests/second API rate limit. |
| **`500 Internal Error`** | Server-side execution exception. | Unhandled runtime failure. |
| **`503 Service Unavailable`** | Upstream database or service unavailable. | Circuit breaker open and fallback unavailable. |

---

### 3. API Endpoints Catalog

#### Group 1: Health Probes & System Diagnostics

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/health` | None (Public) | High-level platform health probe returning uptime, timestamp, and active data source. |
| `GET` | `/api/health/live` | None (Public) | Kubernetes / Docker liveness probe confirming process is alive. |
| `GET` | `/api/health/ready` | None (Public) | Readiness probe confirming application is initialized and accepting requests. |
| `GET` | `/api/health/db` | None (Public) | Granular MySQL connection health, latency check, and circuit breaker status. |
| `GET` | `/api/health/containers` | `operator` | Reports live Docker container fleet status (`novanest-api`, `novanest-db`, etc.). |
| `GET` | `/api/diagnostics/data-source` | `read` | Returns active storage engine (`mysql` vs `csv_fallback`), table record counts, and pool stats. |

#### Group 2: Business Overview & Financial Intelligence

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/overview` | `read` | Master business KPIs: total orders, delivered orders, GMV (₹4.66 Cr), net revenue, AOV, and margin. |
| `GET` | `/api/financial/overview` | `read` | Deep financial metrics: promotional subsidies, gross vs net revenue, and contribution margin waterfall. |
| `GET` | `/api/operations/overview` | `read` | Fleet operations: fulfillment rates, average transit times, zone distributions, and SLA breaches. |
| `GET` | `/api/customer/overview` | `read` | Customer intelligence: cohort retention, RFM segment counts, and active account distribution. |
| `GET` | `/api/restaurant/overview` | `read` | Merchant overview: active restaurants, cuisine breakdowns, and underperforming partners. |

#### Group 3: Entity 360 Deep-Dive Profiles

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/customer/360/{customer_id}` | `read` | Detailed customer profile: order history, RFM scores, LTV, churn risk, and discount eligibility guardrails. |
| `GET` | `/api/restaurant/360/{restaurant_id}` | `read` | Merchant diagnostic: order volume, cancellation rates, kitchen preparation bottlenecks, and action plans. |
| `GET` | `/api/operations/riders` | `read` | Fleet workload list: active riders, completed deliveries, rating, and vehicle classification. |

#### Group 4: Prescriptive Business Intelligence & Governance

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/prescriptive/summary` | `read` | Summary portfolio KPIs: active initiatives count, gross benefit, cost, net impact, and portfolio ROI. |
| `GET` | `/api/prescriptive/recommendations` | `read` | Filterable list of prescriptive recommendations (supports `?domain=...&status=...&priority=...`). |
| `GET` | `/api/prescriptive/recommendations/{id}` | `read` | Detailed recommendation record: problem statement, supporting evidence, action, and financial model. |
| `POST` | `/api/prescriptive/recommendations/{id}/approve` | `operator` | **Human Approval Gate**: Approves recommendation from `PROPOSED` to `APPROVED`. |
| `POST` | `/api/prescriptive/recommendations/{id}/reject` | `operator` | Rejects recommendation with mandatory non-empty `rejection_reason`. |
| `POST` | `/api/prescriptive/recommendations/{id}/start-progress` | `operator` | Advances approved recommendation to `IN_PROGRESS` (fails if not approved). |
| `POST` | `/api/prescriptive/recommendations/{id}/mark-implemented` | `operator` | Advances recommendation from `IN_PROGRESS` to `IMPLEMENTED`. |
| `POST` | `/api/prescriptive/recommendations/{id}/record-outcome` | `operator` | Records audited realized financial gross benefit and actual cost, closing the initiative. |
| `POST` | `/api/prescriptive/simulate` | `operator` | Executes controlled what-if scenario simulation (`is_simulation_projection: True`). |

#### Group 5: Multi-Agent AI & Streaming Chatbot

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/ai/ask` | `read` | Synchronous inquiry execution via Master Orchestrator returning narrative, facts, and recommendations. |
| `POST` | `/api/ai/stream-ticket` | `read` | Generates a 60-second single-use ticket for authenticated SSE streaming. |
| `GET` | `/api/ai/ask/stream` | Valid Ticket | Real-time Server-Sent Events (SSE) stream emitting agent execution lifecycle events and progressive narrative. |
| `GET` | `/api/ai/agents/status` | `read` | Returns registration and operational health status across all 5 domain intelligence agents. |
| `GET` | `/api/ai/traces/{request_id}` | `read` | Retrieves detailed execution span timings, sub-agent durations, and data provenance. |
| `POST` | `/api/ai/reset` | `read` | Clears active conversational memory and remembered entities for the caller's session. |

#### Group 6: Machine Learning & Explainability

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/ml/models` | `read` | Returns Model Registry metadata, active versions, SHA-256 hashes, and confidence tiers. |
| `POST` | `/api/ml/predict/{model_name}` | `read` | Executes inference for target model (e.g. `eta`, `demand`) with empirical confidence intervals. |
| `GET` | `/api/ml/explain/{model_name}` | `read` | Returns global TreeSHAP feature importance rankings and interactive waterfall vectors. |

#### Group 7: Operations, Observability & Disaster Recovery

| Method | Endpoint | Required Scope | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/metrics` | Loopback / Auth | Prometheus metrics export endpoint protected by Bearer token authentication. |
| `GET` | `/api/operations/alerts` | `operator` | Returns recent operational alert event history and webhook dispatch logs. |
| `POST` | `/api/operations/backup` | `admin` | Triggers immediate encrypted database snapshot and HMAC sidecar generation. |
| `POST` | `/api/operations/restore` | `admin` | Initiates restoration testing into isolated verification database (`novanest_restore_isolated`). |

---

### 4. Sample Request & Response Payloads

#### Example 1: Approve Recommendation (`POST /api/prescriptive/recommendations/REC-RET-VIP-001/approve`)

**Headers:**
```http
Authorization: Bearer test-operator-key-phase06-8
Content-Type: application/json
```

**Request Payload:**
```json
{
  "approved_by": "Senior Operations Manager",
  "approval_notes": "Approved for Q4 VIP retention pilot across Bangalore and Chennai."
}
```

**Response Payload (`HTTP 200 OK`):**
```json
{
  "status": "success",
  "recommendation": {
    "recommendation_id": "REC-RET-VIP-001",
    "domain": "customer",
    "priority": "high",
    "title": "VIP High-Value Customer Churn Prevention Campaign",
    "lifecycle_status": "Approved",
    "financial_impact": {
      "projected_gross_benefit": 42500.0,
      "projected_cost": 15000.0,
      "projected_net_benefit": 27500.0,
      "projected_roi_pct": 183.33
    },
    "governance_metadata": {
      "approved_by": "Senior Operations Manager",
      "approval_notes": "Approved for Q4 VIP retention pilot across Bangalore and Chennai.",
      "approved_at": "2026-11-15T09:25:00Z"
    }
  }
}
```

#### Example 2: Conversational AI Query (`POST /api/ai/ask`)

**Headers:**
```http
Authorization: Bearer test-operator-key-phase06-8
Content-Type: application/json
```

**Request Payload:**
```json
{
  "query": "What is our contribution margin in Bangalore and how does it compare to our overall platform?",
  "session_id": "session_exec_001"
}
```

**Response Payload (`HTTP 200 OK`):**
```json
{
  "response": "In Bangalore, NovaNest realized a delivered contribution margin of 24.12% across 12,410 delivered orders, performing slightly above the platform-wide average of 23.59%. This higher margin is driven by denser delivery zones reducing transit fees and a favorable merchant commission mix.",
  "facts": [
    {
      "claim": "Bangalore Delivered Orders: 12,410",
      "data_source": "orders_table",
      "verified": true
    },
    {
      "claim": "Bangalore Delivered Contribution Margin: 24.12%",
      "data_source": "orders_table JOIN restaurants JOIN deliveries",
      "verified": true
    },
    {
      "claim": "Platform Delivered Contribution Margin: 23.59%",
      "data_source": "novanest_db canonical ground truth",
      "verified": true
    }
  ],
  "recommendations": [],
  "session_id": "session_exec_001",
  "execution_metadata": {
    "orchestrator_latency_ms": 34.2,
    "agents_invoked": ["FinancialAgent", "DecisionAgent"]
  }
}
```
