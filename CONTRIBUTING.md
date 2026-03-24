# Contributing Guide

## How to Contribute

We welcome contributions! Here's how to get started.

### Prerequisites
- Git knowledge
- Python 3.11+ and Node.js 18+
- Understanding of the architecture

### Development Setup

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Set up development environment (see SETUP.md)

### Making Changes

#### Backend
Follow PEP 8 style guide:
```bash
# Format code
black app/

# Lint
pylint app/
ruff check app/

# Type check (if using type hints)
mypy app/
```

#### Frontend
Follow ESLint/Prettier:
```bash
npm run lint
npm run type-check
```

### Testing

```bash
# Backend
cd backend
pytest tests/ -v --cov

# Frontend
cd frontend
npm run lint
npm run type-check
```

### Commit Guidelines

Use conventional commits:
```
feat: Add support for Perl language
fix: Fix false positive in eval detection
docs: Update API documentation
test: Add tests for webhook signature verification
refactor: Simplify risk scoring algorithm
```

### Pull Request Process

1. Update documentation
2. Add tests for new functionality
3. Ensure all tests pass
4. Create detailed PR description
5. Link related issues
6. Wait for review

### Reporting Bugs

Include:
- Description and steps to reproduce
- Expected vs actual behavior
- Environment info (OS, Python version, etc.)
- Relevant logs/screenshots

### Requesting Features

Discuss in Issues first. Include:
- Use case and motivation
- Proposed solution
- Alternatives considered
- Implementation notes

### Code Review Process

- At least 1 maintainer approval
- CI/CD checks must pass
- No decreasing test coverage
- Documentation updated

### Maintainers

- Primary: @extremecoder-rgb
- Reviews: Community is welcome

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── analyzers/      # Language-specific analyzers
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── webhooks/       # Webhook handlers
│   │   └── utils/          # Utilities
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client
│   │   ├── store/          # State management
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── CONTRIBUTING.md
```

## Areas for Contribution

- **Language Support**: Add more language analyzers
- **Integrations**: Slack, Discord, email notifications
- **UI/UX**: Dashboard improvements
- **Performance**: Optimization opportunities
- **Documentation**: Guides, examples, tutorials
- **Testing**: Increase test coverage
- **Security**: Vulnerability reports (security@reposhield.io)

## Code of Conduct

- Be respectful
- Assume good intent
- Provide constructive feedback
- No harassment or discrimination
- Report violations to maintainers

## License

All contributions are licensed under MIT License.

---

Thank you for contributing!
