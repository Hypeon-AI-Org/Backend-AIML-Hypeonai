# Backend AIML Hypeonai (Production-Ready FastAPI Backend)

This repository contains a production-ready FastAPI backend with authentication, rate limiting, and health monitoring.

## Key Features

- **Authentication**: Email/password and Google OAuth2 sign-in
- **Rate Limiting**: Protects auth endpoints from abuse
- **Health Checks**: Application and database health monitoring
- **Security**: JWT tokens, secure cookies, password hashing
- **Database**: MongoDB integration with Motor async driver

## Files Added

- `main.py` - app entrypoint with health check endpoints
- `app/` - package with routes, core, models, utils, deps, and schemas
- `app/utils/rate_limiter.py` - rate limiting implementation
- `test_health.py` - health check endpoint tests
- `test_auth_rate_limit.py` - auth endpoint rate limiting tests
- `data/products.example.json` - sample product data
- `scripts/seed_products.py` - small script to seed example data

## Deployment Improvements

- Removed credentials from .env.example
- Added health check endpoints (/health, /health/db)
- Implemented rate limiting on auth endpoints
- Added comprehensive logging

## How to Run (Development)

1. Create a virtualenv and install requirements:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:

```cmd
uvicorn main:app --reload
```

## Health Check Endpoints

- `GET /health` - Basic application health
- `GET /health/db` - Database connectivity health

## Rate Limited Endpoints

- `POST /api/auth/signup` - 5 requests per minute
- `POST /api/auth/login` - 5 requests per minute
- `POST /api/auth/google` - 5 requests per minute
- `POST /api/auth/refresh` - 5 requests per minute
- `POST /api/auth/forgot` - 3 requests per hour
- `POST /api/auth/reset` - 3 requests per hour
