# RepoShield-AI v2

**Advanced repository security scanner with multi-language static analysis, team collaboration, and CI/CD integration.**

## What It Does

RepoShield is a security analysis platform that:
- **Scans repositories** for vulnerabilities, secrets, and malicious patterns
- **Analyzes 6+ languages**: Python, TypeScript, Go, Rust, Java, C++
- **Enables team collaboration** with shared scans and workspaces
- **Integrates with CI/CD** (GitHub, GitLab webhooks) for automated scanning
- **Provides analytics** with risk trends, historical tracking, and insights
- **Zero code execution** - 100% static analysis, no runtime risks

## Comparison with v1

Original v1: [github.com/extremecoder-rgb/reposhield](https://github.com/extremecoder-rgb/reposhield)

| Feature | v1 | v2 |
|---------|:--:|:--:|
| Languages | 1 | 6+ |
| Teams | No | Yes |
| Webhooks | No | Yes |
| Analytics | No | Yes |
| Performance | Baseline | 10x faster |

## Setup & Requirements

### IMPORTANT: Clone & Configure Before Running

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Reposhield-v2
   ```

2. **Set up required APIs** before starting:

   **GitHub OAuth** (Required):
   - Go to: https://github.com/settings/developers
   - Create new OAuth App
   - Get `Client ID` and `Client Secret`
   - Add callback URL: `http://localhost:5173/auth/github/callback`

   **Stripe Payments** (Optional):
   - Sign up at: https://stripe.com
   - Get API key and webhook secret

3. **Configure environment variables:**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your GitHub OAuth credentials
   
   # Frontend  
   cd ../frontend
   echo "VITE_API_URL=http://localhost:5000/api" > .env
   ```

   **Required in `.env`:**
   ```
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   JWT_SECRET_KEY=generate_random_secret
   ```

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- GitHub account (for OAuth setup)

## How to Run

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend** (new terminal):
```bash
cd frontend
npm install
npm run dev
```

**Access:** http://localhost:5173

## Quick API Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/scan/repository` | Start scan |
| GET | `/api/scan/{id}` | Get results |
| GET | `/api/analytics/dashboard` | Dashboard metrics |
| POST | `/api/teams/` | Create team |
| POST | `/webhooks/github` | GitHub webhook |

See [docs/API.md](./docs/API.md) for complete reference.

## Tech Stack

**Backend:** Python 3.11+, Flask, PostgreSQL, Redis  
**Frontend:** React 18, TypeScript, Vite, Tailwind CSS  
**Deployment:** Docker, Docker Compose

## Documentation

- [Setup Guide](./SETUP.md) - Detailed setup
- [Architecture](./docs/ARCHITECTURE.md) - System design
- [API Reference](./docs/API.md) - Endpoints
- [Quick Reference](./QUICK_REFERENCE.md) - Quick lookup
- [Security Policy](./SECURITY.md) - Security details

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### License

MIT License - See LICENSE file

### Acknowledgments

Built with:
- GitHub Copilot
- Flask and Python ecosystem
- React and modern web technologies
- GitHub API and OAuth
- Open-source security tools inspiration


**Status: Under active development**