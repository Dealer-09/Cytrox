# API Documentation - RepoShield-AI v2

## Base URL
```
http://localhost:5000/api
Production: https://reposhield.ai/api
```

## Authentication

All endpoints (except `/auth/github/login` and `/auth/github/callback`) require an `Authorization` header:

```
Authorization: Bearer <access_token>
```

Access tokens are obtained through GitHub OAuth and are valid for 15 minutes.

## Authentication Endpoints

### Initiate GitHub OAuth
```
GET /auth/github/login

Query Parameters:
  redirect_uri (optional): URL to redirect after auth

Response:
{
  "auth_url": "https://github.com/login/oauth/authorize?..."
}
```

### GitHub OAuth Callback
```
POST /auth/github/callback

Body:
{
  "code": "<github_authorization_code>"
}

Response:
{
  "access_token": "<jwt_token>",
  "refresh_token": "<refresh_token>",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "avatar_url": "https://...",
    "subscription_tier": "FREE"
  }
}
```

### Get Current User
```
GET /auth/me

Response:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "avatar_url": "https://...",
  "subscription_tier": "FREE",
  "subscription_active": false,
  "created_at": "2026-03-24T10:00:00"
}
```

### Refresh Access Token
```
POST /auth/refresh

Headers:
  Authorization: Bearer <refresh_token>

Response:
{
  "access_token": "<new_jwt_token>"
}
```

### Logout
```
POST /auth/logout

Response:
{
  "message": "Logged out successfully"
}
```

## Scanning Endpoints

### Start Repository Scan
```
POST /scan/repository

Body:
{
  "repository_url": "https://github.com/owner/repo"
}

Response (202 Accepted):
{
  "scan_id": 123,
  "status": "PENDING",
  "message": "Scan queued successfully"
}

Error (403):
{
  "error": "Premium subscription required for private repos"
}
```

### Get Scan Results
```
GET /scan/<scan_id>

Response:
{
  "id": 123,
  "repository_url": "https://github.com/owner/repo",
  "status": "COMPLETED",
  "risk_score": 150,
  "risk_level": "HIGH",
  "findings": {
    "findings": [
      {
        "type": "DANGEROUS_CALL",
        "severity": "CRITICAL",
        "file_path": "app.py",
        "line_number": 42,
        "message": "Dangerous eval() with user input",
        "code_snippet": "eval(user_input)",
        "recommendation": "Use ast.literal_eval() instead",
        "confidence": 0.95
      }
    ]
  },
  "summary": {
    "total_files": 150,
    "analyzed_files": 120,
    "languages_detected": {
      "python": 85,
      "javascript": 35
    },
    "critical_findings": 1,
    "high_findings": 3
  },
  "scan_duration": 15,
  "created_at": "2026-03-24T10:00:00",
  "completed_at": "2026-03-24T10:00:15"
}

Error (404):
{
  "error": "Scan not found"
}
```

### Get Scan History
```
GET /scan/history

Query Parameters:
  limit: 10 (default)
  offset: 0 (default)

Response:
{
  "scans": [
    {
      "id": 123,
      "repository_url": "https://github.com/owner/repo",
      "risk_level": "HIGH",
      "risk_score": 150,
      "created_at": "2026-03-24T10:00:00",
      "status": "COMPLETED"
    }
  ]
}
```

## Analytics Endpoints

### Dashboard Metrics
```
GET /analytics/dashboard

Response:
{
  "total_scans": 42,
  "average_risk_score": 75.5,
  "risk_distribution": {
    "SAFE": 10,
    "LOW": 15,
    "MEDIUM": 12,
    "HIGH": 4,
    "CRITICAL": 1
  },
  "languages_analyzed": ["python", "javascript", "go"]
}
```

### Scanning Trends
```
GET /analytics/trends

Query Parameters:
  days: 30 (default)

Response:
{
  "trends": [
    {
      "date": "2026-03-24",
      "scan_count": 5,
      "average_risk_score": 80.0
    }
  ]
}
```

### Top Findings
```
GET /analytics/top-findings

Response:
{
  "top_findings": [
    {
      "type": "DANGEROUS_CALL",
      "count": 12
    },
    {
      "type": "EXPOSED_SECRET",
      "count": 8
    }
  ]
}
```

## Team Endpoints

### List Teams
```
GET /teams

Response:
{
  "teams": [
    {
      "id": 1,
      "name": "My Team",
      "slug": "my-team",
      "owner_id": 1,
      "members_count": 3
    }
  ]
}
```

### Create Team
```
POST /teams

Body:
{
  "name": "My Team",
  "slug": "my-team",
  "description": "Team description"
}

Response (201):
{
  "team_id": 1
}
```

### List Team Members
```
GET /teams/<team_id>/members

Response:
{
  "members": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    }
  ]
}
```

### Add Team Member
```
POST /teams/<team_id>/members

Body:
{
  "username": "jane_doe"
}

Response (201):
{
  "message": "Member added"
}
```

## User Endpoints

### Get User Profile
```
GET /users/<user_id>

Response:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "avatar_url": "https://...",
  "subscription_tier": "FREE",
  "created_at": "2026-03-24T10:00:00"
}
```

### Get Current User Profile
```
GET /users/profile

Response:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "avatar_url": "https://...",
  "subscription_tier": "FREE",
  "subscription_active": false
}
```

### Update User Profile
```
PUT /users/profile

Body:
{
  "email": "newemail@example.com"
}

Response:
{
  "message": "Profile updated"
}
```

## Webhook Endpoints

### GitHub Webhook
```
POST /webhooks/github

Headers:
  X-Hub-Signature-256: sha256=<signature>
  X-GitHub-Event: <event_type>

Body:
{
  "action": "opened",
  "repository": {
    "html_url": "https://github.com/owner/repo"
  },
  ...
}

Response:
{
  "message": "Webhook received"
}

Supported Events:
- push: Automatic scan triggered
- pull_request: Optional scan
- schedule: Cron-triggered scan
```

### GitLab Webhook
```
POST /webhooks/gitlab

Headers:
  X-Gitlab-Token: <webhook_secret_token>
  X-Gitlab-Event: <event_type>

Body:
{
  "event_name": "push",
  "project": {
    "web_url": "https://gitlab.com/owner/repo"
  },
  ...
}

Response:
{
  "message": "Webhook received"
}
```

## Health Check

```
GET /health

Response:
{
  "status": "healthy",
  "service": "RepoShield-AI v2"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Repository URL required"
}
```

### 401 Unauthorized
```json
{
  "error": "Missing or invalid authorization"
}
```

### 403 Forbidden
```json
{
  "error": "Premium subscription required for private repos"
}
```

### 404 Not Found
```json
{
  "error": "Scan not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An error occurred while processing your request"
}
```

## Rate Limiting

Free tier: 100 scans/hour
Premium tier: Unlimited

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1711270800
```

## Pagination

List endpoints support pagination:
```
GET /endpoint?limit=10&offset=0

limit: Number of results (default: 10, max: 100)
offset: Starting position (default: 0)
```

## Filtering

Supported filters vary by endpoint:
```
GET /scan/history?status=COMPLETED&risk_level=HIGH&limit=10
```

## Sorting

Some endpoints support sorting:
```
GET /scan/history?sort=-created_at
(- prefix for descending)
```

## Data Types

### Risk Levels
- SAFE (0-20 points)
- LOW (21-50 points)
- MEDIUM (51-100 points)
- HIGH (101-200 points)
- CRITICAL (201+ points)

### Severity Levels
- INFO
- LOW
- MEDIUM
- HIGH
- CRITICAL

### Subscription Tiers
- FREE (public repos only)
- PRO ($9.99/month)
- ENTERPRISE (custom pricing)

---

For more information, see [Architecture Guide](./ARCHITECTURE.md) or [Setup Guide](../SETUP.md).
