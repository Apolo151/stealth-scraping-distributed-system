```mermaid
graph TB
    subgraph "Producer Layer"
        P[Producer Service<br/>Creates Tasks]
    end

    subgraph "Message Queue - RabbitMQ"
        RMQ[RabbitMQ Cluster<br/>3 Nodes]
        WQ[Work Queue]
        DLQ[Dead Letter Queue<br/>Failed Tasks]
        
        RMQ --> WQ
        WQ -.Failed.-> DLQ
    end

    subgraph "Worker Layer"
        W1[Worker 1]
        W2[Worker 2]
        WN[Worker N<br/>Auto-scaled]
    end

    subgraph "Database"
        DB[(SQL Database<br/>Primary + Replica)]
    end

    subgraph "Monitoring Stack"
        PROM[Prometheus<br/>Metrics]
        GRAF[Grafana<br/>Dashboards]
        ELK[ELK Stack<br/>Logs]
        SENTRY[Sentry<br/>Errors]
        
        PROM --> GRAF
    end

    subgraph "External"
        TARGETS[Target Websites]
    end

    %% Main Data Flow
    P -->|Publish Tasks| RMQ
    WQ -->|Consume| W1
    WQ -->|Consume| W2
    WQ -->|Consume| WN
    
    W1 -->|Scrape| TARGETS
    W2 -->|Scrape| TARGETS
    WN -->|Scrape| TARGETS
    
    W1 -->|Store Results| DB
    W2 -->|Store Results| DB
    WN -->|Store Results| DB

    %% Monitoring Integration
    P -.Metrics.-> PROM
    RMQ -.Metrics.-> PROM
    W1 -.Metrics.-> PROM
    W2 -.Metrics.-> PROM
    WN -.Metrics.-> PROM
    DB -.Metrics.-> PROM
    
    W1 -.Logs.-> ELK
    W2 -.Logs.-> ELK
    WN -.Logs.-> ELK
    
    W1 -.Errors.-> SENTRY
    W2 -.Errors.-> SENTRY
    WN -.Errors.-> SENTRY

    %% Orchestration
    K8S[Kubernetes<br/>Auto-scaling & Recovery]
    K8S -.Manages.-> W1
    K8S -.Manages.-> W2
    K8S -.Manages.-> WN

    style P fill:#4A90E2
    style RMQ fill:#FF6B6B
    style W1 fill:#48C774
    style W2 fill:#48C774
    style WN fill:#48C774
    style DB fill:#9B59B6
    style PROM fill:#E67E22
    style GRAF fill:#F39C12
    style ELK fill:#16A085
    style SENTRY fill:#E74C3C
    style K8S fill:#3498DB
```

## Architecture Overview

### Core Components
- **Producer**: Generates scraping tasks and publishes to queue
- **RabbitMQ Cluster**: Message broker with 3-node cluster for high availability
- **Worker Nodes**: Stateless containers that consume tasks and scrape websites (horizontally scalable)
- **SQL Database**: Stores results with primary-replica setup
- **Monitoring**: Prometheus/Grafana (metrics), ELK Stack (logs), Sentry (errors)
- **Kubernetes**: Orchestrates worker scaling and recovery

### Key Features
- **Horizontal Scaling**: Add/remove worker nodes based on load
- **High Availability**: RabbitMQ clustering, database replication
- **Dead Letter Queue**: Failed tasks for retry or manual intervention
- **Comprehensive Monitoring**: Metrics, logs, and error tracking from all components
- **Auto-scaling**: Kubernetes manages worker lifecycle based on queue depth