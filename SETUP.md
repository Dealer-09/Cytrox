# Setup Guide - RepoShield-AI v2

## Local Development Setup (5-10 minutes)

### 1. Clone Repository
```bash
git clone <repo-url>
cd Reposhield-v2
```

### 2. GitHub OAuth Setup

1. Go to GitHub Settings › Developer settings › OAuth Apps
2. Create new OAuth App with:
   - Application name: `RepoShield-AI`
   - Homepage URL: `http://localhost:5173`
   - Authorization callback URL: `http://localhost:5173/auth/github/callback`
3. Note your `Client ID` and `Client Secret`

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy and configure environment
cp .env.example .env

# Edit .env file
nano .env
# Add:
# GITHUB_CLIENT_ID=<your_client_id>
# GITHUB_CLIENT_SECRET=<your_client_secret>
# JWT_SECRET_KEY=<generate_random_secret>

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run backend
python main.py
```

Backend will be available at `http://localhost:5000`

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:5000/api" > .env

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 5. Verify Installation

1. Open http://localhost:5173 in browser
2. Click "Login with GitHub"
3. You should be redirected to GitHub OAuth
4. After authorization, you'll be on the dashboard

## Docker Setup

```bash
# Create .env file
cp backend/.env.example .env
# Edit .env with credentials

# Start all services
docker-compose up -d

# Create database (run once)
docker-compose exec backend python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Database Setup

### SQLite (Development - Default)
Automatically created on first run as `reposhield.db`

### PostgreSQL (Production)

```bash
# Install PostgreSQL locally or use Docker:
docker run -d \
  --name reposhield-db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=reposhield \
  -p 5432:5432 \
  postgres:15

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/reposhield
```

## Stripe Setup (Optional - for Payments)

1. Go to https://dashboard.stripe.com
2. Get your API key and webhook secret
3. Add to .env:
```
STRIPE_API_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Clear cache and reinstall
pip cache purge
pip install -r requirements.txt --force-reinstall
```

### Frontend won't connect to backend
```bash
# Check CORS is enabled in backend
# Check API_URL in frontend .env
# Verify backend is running on port 5000

# Test backend health
curl http://localhost:5000/health
```

### Database errors
```bash
# Reset database
rm reposhield.db  # SQLite

# or for PostgreSQL
dropdb reposhield
createdb reposhield
```

### GitHub OAuth not working
- Verify Client ID/Secret in .env
- Check callback URL matches exactly
- Clear browser cookies and try again

## Development Commands

### Backend
```bash
# Run with debug mode
FLASK_DEBUG=True python main.py

# Run tests
pytest tests/ -v

# Run linting
pylint app/
ruff check app/

# Format code
black app/
```

### Frontend
```bash
# Development with hot reload
npm run dev

# Build for production
npm run build

# Preview build
npm run preview

# Lint code
npm run lint

# Type checking
npm run type-check
```

## Next Steps

1. Read [Architecture Guide](./docs/ARCHITECTURE.md)
2. Check [API Documentation](./docs/API.md)
3. Review [Security Policy](./SECURITY.md)
4. Set up CI/CD webhooks using [API Documentation](./docs/API.md)

## Support

For issues or questions:
1. Check GitHub Issues
2. Review documentation
3. Check logs: `docker logs <service_name>`
