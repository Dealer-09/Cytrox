# Quick Reference Guide

## Project Structure Overview

```
Reposhield-v2/
├── backend/
│   ├── app/
│   │   ├── analyzers/          # Multi-language analysis modules
│   │   │   ├── __init__.py     # Orchestrator
│   │   │   ├── python_analyzer.py
│   │   │   ├── typescript_analyzer.py
│   │   │   └── go_analyzer.py  # Plus: rust, java, cpp
│   │   │
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   └── __init__.py     # User, Team, Scan, Finding, etc
│   │   │
│   │   ├── routes/             # Flask API endpoints
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── scan.py         # Scanning
│   │   │   ├── analytics.py    # Analytics
│   │   │   ├── users.py        # User management
│   │   │   ├── teams.py        # Team collaboration
│   │   │   ├── webhooks.py     # CI/CD webhooks
│   │   │   └── health.py       # Health checks
│   │   │
│   │   ├── utils/              # Utility functions
│   │   └── __init__.py         # App factory
│   │
│   ├── tests/                  # Unit & integration tests
│   ├── main.py                 # Entry point
│   ├── requirements.txt        # Dependencies
│   ├── Dockerfile              # Container image
│   └── .env.example            # Configuration template
│
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   └── Navigation.tsx
│   │   │
│   │   ├── pages/              # Page components
│   │   │   ├── Auth.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Scan.tsx
│   │   │   ├── ScanHistory.tsx
│   │   │   ├── ScanResults.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Team.tsx
│   │   │
│   │   ├── api/                # API client
│   │   │   └── client.ts
│   │   │
│   │   ├── store/              # State management
│   │   │   └── authStore.ts
│   │   │
│   │   ├── main.tsx            # React entry point
│   │   ├── App.tsx             # Root component
│   │   ├── index.css           # Global styles
│   │   └── App.css             # App styles
│   │
│   ├── index.html              # HTML template
│   ├── package.json            # Dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── tailwind.config.js      # Tailwind CSS
│   ├── postcss.config.js       # PostCSS
│   ├── Dockerfile              # Container image
│   └── nginx.conf              # Nginx config (production)
│
├── docs/
│   ├── ARCHITECTURE.md         # System design
│   └── API.md                  # API reference
│
├── docker-compose.yml          # Container orchestration
├── README.md                   # Project overview
├── SETUP.md                    # Setup instructions
├── ENHANCEMENT_SUMMARY.md      # What's new in v2
├── CONTRIBUTING.md            # Contribution guidelines
├── SECURITY.md               # Security policy
├── LICENSE                    # MIT License
└── .gitignore                # Git ignore rules
```

## Quick Start

### 1. Backend Setup (2 minutes)
```bash
cd backend
cp .env.example .env
# Edit .env with GitHub OAuth credentials
pip install -r requirements.txt
python main.py
```
Backend ready at `http://localhost:5000`

### 2. Frontend Setup (1 minute)
```bash
cd frontend
npm install
npm run dev
```
Frontend ready at `http://localhost:5173`

### 3. Access Application
Open http://localhost:5173 → Click "Login with GitHub"

## Core Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python 3.11+ | Server logic |
| API | Flask | Web framework |
| Database | PostgreSQL | Data persistence |
| Cache | Redis | Performance |
| Frontend | React 18 | UI framework |
| Build | Vite | Fast bundling |
| Styling | Tailwind CSS | Utility CSS |
| State | Zustand | State management |

## Key Features at a Glance

### Multi-Language Analysis
- Python (AST-based)
- TypeScript (Regex patterns)
- Go, Rust, Java, C++ (Pattern matching)

### Team Collaboration
- Create teams
- Invite members
- Share scans
- Role-based access

### CI/CD Integration
- GitHub webhooks
- GitLab webhooks
- Push event triggers
- Webhook logs

### Analytics
- Dashboard metrics
- Trend analysis
- Top findings
- Historical tracking

### Subscriptions
- Free (public repos)
- Pro ($9.99/month)
- Enterprise (custom)

## API Quick Reference

All API endpoints below are relative to `http://localhost:5000/api`.

### Authentication
```
GET  /api/auth/github/login           # Start OAuth
POST /api/auth/github/callback        # OAuth callback
GET  /api/auth/me                     # Current user
POST /api/auth/refresh                # Refresh token
```

### Scanning
```
POST /api/scan/repository             # Start scan
GET  /api/scan/{id}                   # Get results
GET  /api/scan/history                # Scan history
```

### Analytics
```
GET  /api/analytics/dashboard         # Dashboard metrics
GET  /api/analytics/trends            # Trends
GET  /api/analytics/top-findings      # Top findings
```

### Teams
```
GET  /api/teams/                      # List teams
POST /api/teams/                      # Create team
GET  /api/teams/{id}/members          # List members
POST /api/teams/{id}/members          # Add member
```

## Development Commands

### Backend
```bash
cd backend

# Run
python main.py

# Test
pytest tests/ -v

# Lint
pylint app/
ruff check app/

# Format
black app/
```

### Frontend
```bash
cd frontend

# Dev
npm run dev

# Build
npm run build

# Lint
npm run lint

# Type check
npm run type-check
```

## Database Models

```
User
├── GitHub authentication
├── Subscription management
└── Teams & Scans

Team
├── Owner
└── Members (many-to-many)

Scan
├── User/Team
├── Repository URL
├── Status (PENDING, RUNNING, COMPLETED, FAILED)
├── Risk Score & Level
└── Findings (JSON)

Finding
├── Type (DANGEROUS_CALL, SECRET, etc)
├── Severity
├── File & Line
└── Recommendation

WebhookLog
├── Provider (GitHub, GitLab)
├── Event Type
└── Associated Scan
```

## Environment Variables

### Backend (.env)
```
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
JWT_SECRET_KEY=xxx
DATABASE_URL=postgresql://user:pass@localhost/reposhield
REDIS_URL=redis://localhost:6379/0
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000/api
```

## Common Tasks

### Create a Scan
```javascript
const response = await api.post('/scan/repository', {
  repository_url: 'https://github.com/owner/repo'
});
```

### Get Scan Results
```javascript
const scan = await api.get(`/scan/${scanId}`);
```

### Fetch Analytics
```javascript
const analytics = await api.get('/analytics/dashboard');
```

### Create Team
```javascript
const team = await api.post('/teams', {
  name: 'My Team',
  slug: 'my-team'
});
```

## Deployment Options

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Backend
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 main:app

# Frontend
npm run build
# Serve dist/ folder
```

## Troubleshooting

### Backend won't start
```bash
python --version  # Check 3.11+
pip install -r requirements.txt --force-reinstall
```

### Frontend can't connect
```bash
# Check backend health
curl http://localhost:5000/health

# Check VITE_API_URL
cat frontend/.env
```

### Database errors
```bash
# Reset SQLite
rm backend/reposhield.db

# Reset PostgreSQL
dropdb reposhield && createdb reposhield
```

## Resources

- [README.md](./README.md) - Project overview
- [SETUP.md](./SETUP.md) - Detailed setup guide
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System design
- [API.md](./docs/API.md) - API documentation
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contributing guide
- [SECURITY.md](./SECURITY.md) - Security policy

## Getting Help

1. Check documentation in `/docs`
2. Search GitHub Issues
3. Check logs: `docker logs <service>`
4. Review code comments
5. Ask in GitHub Discussions

---

**Happy scanning!**
