# System Architecture: Financial Market Data & Analytics

This project utilizes a **Serverless AWS Architecture** designed to handle real-time stock searches, automated market data synchronization, and secure user trade management.

---

## Core Components

### 1. Entry Point & Security (AWS Public Zone)
* **Amazon API Gateway:** The central HTTPS REST API entry point. It manages client requests, identifies clients, and routes traffic to the appropriate backend services.
* **AWS WAF (Web Application Firewall):** Provides a security layer with Web ACLs to protect the API from common web exploits and unauthorized access.
* **Identity & Access Management:** * **API Keys & Usage Plans:** Enforces quotas and tracking per application/client.
    * **AWS IAM:** Handles fine-grained Authorization (AuthZ) for backend roles.

### 2. Application Logic & Compute (AWS VPC)
* **Market Data Service (AWS Lambda):** Orchestrates stock searches by name, symbol, or group. It queries the database and formats data for the mobile client.
* **Indexes Update Service (AWS Lambda):** A specialized background worker responsible for periodic market data refreshes and synchronization with external providers.
* **NAT Gateway:** Positioned in the public subnet to allow Lambda functions residing in private subnets to securely perform outbound HTTPS calls to external APIs.

### 3. Data Layer & Storage
* **Amazon RDS for PostgreSQL:** The primary relational engine. It manages structured data across several key tables: `Stocks`, `StockQuotes`, `IndexGroups`, `UserTrades`, `UserQueries`, and `UserWatchlist`.
* **Security Groups:** Act as a virtual firewall, explicitly allowing Lambda-to-RDS traffic on port 5432 while strictly denying any direct inbound traffic from the public internet.

### 4. Event Orchestration (Amazon EventBridge)
* **Scheduled Triggers:** **Amazon EventBridge** acts as the system's scheduler. It is configured with a **Scheduled Rule** (e.g., triggering every 5 minutes) to invoke the "Indexes Update Service" automatically.
* **Event-Driven Flow:** Decouples the scheduling logic from the application code, ensuring reliable and serverless execution of routine data maintenance tasks.

### 5. Monitoring, Observability & Configuration
* **Amazon CloudWatch:**
    * **Logs:** Centralized logging for API Gateway execution, Lambda function logs, and update service traces.
    * **Metrics:** Real-time dashboards and alarms to monitor system health and performance.
* **AWS X-Ray:** Provides end-to-end distributed tracing, allowing for deep analysis of request latency and bottlenecks across the serverless stack.
* **Governance & Secrets:**
    * **AWS Secrets Manager:** Manages sensitive data such as Database credentials and External Market Data API keys.
    * **AWS Systems Manager (Parameter Store):** Stores non-sensitive application configurations, including TTL (Time-to-Live) settings and feature flags.

---



### Tech Stack & Integrations

| Category | AWS Service / Integration | Description |
| :--- | :--- | :--- |
| **Compute** | **AWS Lambda** (Python/Node.js) | Serverless execution for market data processing and indexing. |
| **Database** | **Amazon RDS (PostgreSQL)** | Relational storage for stocks, trades, and user watchlists. |
| **Networking** | **VPC, NAT Gateway & API Gateway** | Secure network isolation with a managed HTTPS entry point. |
| **Event Routing** | **Amazon EventBridge** | Serverless event bus for scheduled data refresh triggers. |
| **External APIs** | **Yahoo Finance / Alpha Vantage** | Integration with third-party providers for real-time market data. |
| **Security** | **IAM, WAF & Secrets Manager** | Identity management, web protection, and secure credential storage. |
| **Observability** | **CloudWatch & AWS X-Ray** | Monitoring, logging, and end-to-end distributed tracing. |


