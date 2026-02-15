# System Design

This document outlines the design of a scalable and reliable distributed web scraping system.

## Architecture Overview
The system is designed as a microservices producer-consumer architecture with the following components:

### Core Components
1. **Producer Service**: Generates scraping tasks and pushes them to RabbitMQ
2. **RabbitMQ Message Queue**: Distributed message broker for reliable task distribution and delivery
3. **Worker Nodes**: Horizontally scalable consumer instances that process scraping tasks
4. **SQL Database**: Stores scraped data, task metadata, and system state
5. **Monitoring Stack**: Comprehensive observability layer for system health and performance

## Message Queue (RabbitMQ)
- **Task Distribution**: Uses work queues pattern for load balancing across workers
- **Durability**: Messages and queues persist through broker restarts
- **Acknowledgments**: Manual ACK ensures tasks aren't lost on worker failure
- **Dead Letter Exchange**: Failed tasks routed to DLX for retry or manual intervention
- **Priority Queues**: Support for task prioritization based on urgency

## Worker Node Architecture
### Horizontal Scaling
- **Stateless Design**: Workers maintain no local state, allowing unlimited horizontal scaling
- **Auto-scaling**: Add/remove workers based on queue depth and CPU utilization
- **Load Balancing**: RabbitMQ round-robin distribution ensures even task allocation
- **Containerization**: Docker containers enable easy deployment and scaling

### Worker Features
- **Idempotent Operations**: Safe retries without duplicate data
- **Graceful Shutdown**: Workers finish current tasks before terminating
- **Resource Limits**: CPU and memory constraints prevent resource exhaustion
- **Concurrent Processing**: Each worker handles multiple tasks using async/threading

## SQL Database
- **Schema Design**: 
  - `tasks` table: Task metadata, status, retries, timestamps
  - `scraped_data` table: Actual scraped content with foreign key to tasks
  - `worker_status` table: Worker health and performance metrics
- **Indexing**: Optimized indexes on task status, timestamps, and URLs
- **Connection Pooling**: Efficient database connection management
- **Transactions**: ACID compliance for data integrity

## Monitoring Stack

### System Health Monitoring
- **Health Check Endpoints**: HTTP endpoints on all services (Producer, Workers, RabbitMQ)
- **Heartbeat Mechanism**: Workers send periodic heartbeats to monitoring service
- **Service Status Dashboard**: Real-time view of all component health states
- **Alerting**: Automated alerts for service failures (e.g., via email/Slack)

**Metrics Collected**:
- Service uptime/downtime
- Worker availability count
- RabbitMQ broker status
- Database connection status

### System Load Monitoring
- **Queue Metrics**:
  - Queue depth (pending tasks)
  - Message publish rate
  - Message consumption rate
  - Consumer utilization percentage
- **Worker Metrics**:
  - Active workers count
  - Tasks processed per minute
  - Average task duration
  - Worker CPU and memory usage
- **Database Metrics**:
  - Connection pool utilization
  - Query execution time
  - Disk usage and I/O

**Visualization**: Grafana dashboards with real-time graphs and historical trends

### Error Logging
- **Centralized Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
  - Elasticsearch: Log storage and indexing
  - Logstash: Log aggregation and parsing
  - Kibana: Log visualization and search interface
- **Structured Logging**: JSON format with context (worker_id, task_id, timestamp)
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Error Categories**:
- Network errors (timeouts, connection failures)
- Scraping errors (CAPTCHA, rate limits, blocked IPs)
- Database errors (connection failures, constraint violations)
- System errors (OOM, disk full)

### Monitoring Tools Integration
```
┌─────────────┐
│ Prometheus  │ ← Metrics collection and storage
└─────────────┘
       ↓
┌─────────────┐
│  Grafana    │ ← Visualization and dashboards
└─────────────┘
       ↓
┌─────────────┐
│ Alertmanager│ ← Alert routing and notification
└─────────────┘

┌─────────────┐
│ ELK Stack   │ ← Log aggregation and analysis
└─────────────┘
```

## Failover and Recovery Mechanisms

### RabbitMQ Failover
- **Clustering**: Multi-node RabbitMQ cluster for high availability
- **Mirrored Queues**: Queue replication across cluster nodes
- **Automatic Failover**: Standby nodes take over on primary failure
- **Connection Recovery**: Automatic reconnection with exponential backoff

### Worker Failover
- **Task Timeout**: Tasks not ACK'd within timeout return to queue
- **Retry Logic**: 
  - Exponential backoff: 1min → 5min → 15min → 1hr
  - Max retry limit: 5 attempts before moving to DLX
- **Health Checks**: Unhealthy workers removed from pool automatically
- **Circuit Breaker**: Prevents cascading failures by temporarily stopping requests

### Database Failover
- **Replication**: Master-slave replication for read scaling and backup
- **Automatic Failover**: Promote slave to master on primary failure
- **Connection Retry**: Workers retry database connections with backoff
- **Data Backup**: Automated daily backups with point-in-time recovery

### Service Recovery
- **Orchestration**: Kubernetes for automatic container restart
- **Rolling Updates**: Zero-downtime deployments with health checks
- **Rollback Strategy**: Quick rollback to previous version on deployment failure
- **State Recovery**: Workers resume from last checkpoint on restart

## Security
- **Authentication**: API keys for producer service, worker registration tokens
- **Authorization**: Role-based access control (RBAC) for different services
- **Encryption**: TLS/SSL for all inter-service communication
- **Secrets Management**: Vault or AWS Secrets Manager for credentials
- **Rate Limiting**: Prevent abuse of producer API endpoints

## Scalability
- **Horizontal Scaling**: Add workers to handle increased load (auto-scaling enabled)
- **Vertical Scaling**: Increase worker resources (CPU/memory) for complex tasks
- **Database Sharding**: Partition data by time or domain for large datasets
- **RabbitMQ Clustering**: Scale message broker horizontally for high throughput
- **Caching Layer**: Redis for frequently accessed data (optional)

## Conclusion
This system design provides a robust, production-ready framework for distributed web scraping with comprehensive monitoring, automatic failover, and horizontal scalability. The architecture ensures high availability, data integrity, and operational visibility through modern DevOps practices.