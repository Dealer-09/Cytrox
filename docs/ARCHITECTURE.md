# Architecture Guide - RepoShield-AI v2

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND LAYER                             │
│                   (React 18 + Vite + Tailwind)                   │
│  - Dashboard, Scanning, Results, Analytics, Team Management     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
              ┌──────────────┴──────────────┐
              │                             │
┌─────────────▼────────────────────┐  ┌────▼──────────────────────────┐
│    API GATEWAY (Flask)           │  │  WEBHOOK RECEIVER              │
│  - Rate Limiting                 │  │  - GitHub Events              │
│  - CORS                          │  │  - GitLab Events              │
│  - JWT Auth                      │  │  - Jenkins Hooks              │
└─────────────┬────────────────────┘  └────┬──────────────────────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│                                                                  │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Auth Service  │  │Scan Service  │  │Analytics Service │    │
│  │ - OAuth       │  │ - Orchestrate│  │ - Trends         │    │
│  │ - JWT         │  │ - Analyze    │  │ - Statistics     │    │
│  │ - Sessions    │  │ - Score      │  │ - Reporting      │    │
│  └───────────────┘  └──────────────┘  └──────────────────┘    │
│                                                                  │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Team Service  │  │Payment Service│ │Webhook Service  │    │
│  │ - CRUD        │  │ - Subscriptions  │ - Verification  │    │
│  │ - Permissions │  │ - Transactions   │ - Routing       │    │
│  └───────────────┘  └──────────────┘  └──────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               ANALYSIS ENGINE (Multi-Language)                   │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐           │
│  │Python Analyzer   TypeScript   │Go Analyzer    │           │
│  │─ AST Parsing     Analyzer     │─ Pattern Match│           │
│  │─ Dangerous Calls │─ Regex     │─ Buffer Risks │           │
│  │─ Secret Detection│─ XSS Check │               │           │
│  └──────────────┘ └──────────────┘ └───────────────┘           │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐           │
│  │Rust Analyzer │ │Java Analyzer │ │C++ Analyzer  │           │
│  │─ Unsafe Code │ │─ SQL Injection  │─ Buffer Overflow        │
│  │─ Memory Risks│ │─ Reflection  │ │─ String Issues│           │
│  └──────────────┘ └──────────────┘ └───────────────┘           │
│                                                                  │
│  Risk Scoring Engine                                            │
│  ─ Weighted calculation                                         │
│  ─ Finding deduplication                                       │
│  ─ Context awareness                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
┌─────────────▼──────────────┐  ┌──────────▼─────────────────┐
│   PERSISTENCE LAYER        │  │   CACHE LAYER (Redis)      │
│                            │  │                            │
│ ┌──────────────────────┐  │  │ ┌──────────────────────┐  │
│ │   PostgreSQL         │  │  │ │ Session Cache        │  │
│ │ ├─ Users             │  │  │ │ GitHub Token Cache   │  │
│ │ ├─ Teams             │  │  │ │ Scan Results Cache   │  │
│ │ ├─ Scans             │  │  │ │ Analytics Cache      │  │
│ │ ├─ Findings          │  │  │ │ Rate Limit Counters  │  │
│ │ ├─ Payments          │  │  │ └──────────────────────┘  │
│ │ └─ Webhooks          │  │  │                             │
│ └──────────────────────┘  │  │ TTL: 5min - 24hours        │
│                            │  │                             │
│ Backups: Daily             │  │                             │
│ Retention: 30 days         │  │                             │
└────────────────────────────┘  └──────────────────────────┘
```

## Request Flow

### Scan Request
```
1. User Input (Frontend)
   ↓
2. API Endpoint: POST /api/scan/repository
   ↓
3. Authentication Check (JWT)
   ↓
4. Access Control (Public vs Private / Subscription)
   ↓
5. Create Scan Record (DB)
   ↓
6. Queue Async Task
   ├─ Clone Repository (Git)
   ├─ Discover Files (Walk directory)
   └─ Parallel Analysis (6 language analyzers)
      ├─ Python Analyzer (AST)
      ├─ TypeScript Analyzer (Regex)
      ├─ Go Analyzer
      ├─ Rust Analyzer
      ├─ Java Analyzer
      └─ C++ Analyzer
   ↓
7. Risk Scoring
   ├─ Weight findings
   ├─ Deduplicate
   └─ Calculate total score
   ↓
8. Store Results (DB)
   ├─ Update Scan record
   ├─ Store findings
   ├─ Cache summary
   └─ Log analytics
   ↓
9. Response to User (WebSocket/HTTP)
```

### Webhook Flow
```
1. GitHub/GitLab sends webhook
   ↓
2. Webhook Receiver: POST /webhooks/{provider}
   ↓
3. Signature Verification (HMAC-SHA256)
   ↓
4. Log Webhook Event (DB)
   ↓
5. Extract Repository URL
   ↓
6. Determine Scan Trigger
   ├─ Push event → Scan triggered
   ├─ PR event → Optional
   └─ Schedule → Cron job
   ↓
7. Create Anonymous Scan
   (Or associate with webhook user if authenticated)
   ↓
8. Queue Analysis (same as scan flow)
```

## Database Schema

### Users Table
```sql
- id (PK)
- github_id (UK)
- username (UK)
- email (UK)
- avatar_url
- subscription_tier (FREE/PRO/ENTERPRISE)
- subscription_active
- subscription_expires
- created_at
- updated_at
- last_login
```

### Teams Table
```sql
- id (PK)
- name
- slug (UK)
- description
- owner_id (FK → users)
- created_at
- updated_at
```

### Scans Table
```sql
- id (PK)
- user_id (FK → users)
- team_id (FK → teams)
- repository_url
- repository_owner
- repository_name
- status (PENDING/RUNNING/COMPLETED/FAILED)
- risk_score
- risk_level
- findings (JSON)
- summary (JSON)
- scan_duration
- total_files
- analyzed_files
- languages_detected (JSON)
- created_at
- completed_at
```

### Findings Table
```sql
- id (PK)
- scan_id (FK → scans)
- type (DANGEROUS_CALL, SECRET, etc)
- severity
- file_path
- line_number
- code_snippet
- message
- recommendation
- confidence
- created_at
```

## API Versioning

Current version: `v2` (v1 deprecated)

Endpoints follow: `/api/v2/{resource}/{action}`

For backward compatibility, `/api/{resource}` routes to latest version.

## Performance Optimization

### Caching Strategy
- **User Sessions**: 15 min (Redis)
- **GitHub Tokens**: 1 hour (Redis, encrypted)
- **Scan Results**: 24 hours (Redis)
- **Analytics Data**: 1 hour (Redis)

### Scalability
- Async background tasks via Celery
- Database connection pooling
- CDN for static assets
- Horizontal scaling ready

### Resource Limits
- Max repo size: 1000 MB
- Scan timeout: 300 seconds
- Rate limit: 100 scans/hour (Free), Unlimited (Premium)
- Max findings per scan: 10,000

## Security Architecture

### Authentication
- **OAuth 2.0**: GitHub authentication
- **JWT**: Stateless sessions
  - Access token: 15 min
  - Refresh token: 7 days
- **CSRF Protection**: State parameter

### Data Protection
- **In Transit**: HTTPS only
- **At Rest**: PostgreSQL encryption
- **Tokens**: AES-256 encryption (GitHub tokens)
- **Secrets**: Environment variables, never logged

### Access Control
- **Public Repos**: No auth required
- **Private Repos**: Premium only
- **Teams**: Role-based (owner, member)
- **API**: Rate limiting + quota

## Deployment Architecture

### Development
- Single machine
- SQLite database
- In-memory cache

### Production
- Load balancer (Nginx/HAProxy)
- Multiple backend instances (3+)
- Managed PostgreSQL (AWS RDS)
- Redis cluster (Elasticache)
- S3 for backups
- CloudFront for frontend CDN

### High Availability
- Auto-scaling groups
- Database failover
- Multi-region support
- Disaster recovery plan

## Monitoring & Logging

### Metrics
- Request latency
- Error rates
- Scan success rate
- Database query time
- Cache hit ratio

### Logging
- Application logs (JSON format)
- Access logs (Nginx)
- Security logs (Auth events)
- Audit logs (Admin actions)

### Alerting
- High error rate (>5%)
- Slow response time (>2s)
- Database connection issues
- Out of memory
- Disk space low

## Technology Decisions

### Why These Technologies?

**Flask over FastAPI**
- Simpler, mature ecosystem
- Better for mixed sync/async workloads
- Excellent extensions (SQLAlchemy, JWT)

**PostgreSQL over MongoDB**
- Strong ACID guarantees
- Better for relational data (teams, findings)
- Better query optimization

**Redis over Memcached**
- Data structure operations
- Persistence options
- Better for rate limiting

**React over Vue/Svelte**
- Larger ecosystem
- Better TypeScript support
- More job market demand

**Tailwind CSS over styled-components**
- Faster development
- Smaller bundle size
- Better performance
