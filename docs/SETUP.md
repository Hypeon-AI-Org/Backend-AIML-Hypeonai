# Setup & Installation

## Prerequisites

- Python 3.8+
- MongoDB (local, cloud, or Docker)
- Git
- pip (Python package manager)
- Virtual environment tool (venv)

## Quick Start

```bash
# 1. Clone and navigate
git clone <repository-url>
cd Backend-AIML-Hypeonai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your actual values

# 5. Start backend
uvicorn main:app --reload

# 6. Verify it's working
curl http://localhost:8000/healthz
# Should return: {"status": "ok"}
```

---

## Detailed Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Backend-AIML-Hypeonai
```

### 2. Create Virtual Environment

**On macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (cmd)**:
```cmd
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell)**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Verify activation - prompt should show `(venv)` prefix.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `fastapi` (0.121.1) — Web framework
- `uvicorn` (0.22.0) — ASGI server
- `motor` (3.4.0) — Async MongoDB driver
- `pymongo` (4.6.3) — MongoDB client
- `passlib[bcrypt]` (1.7.4) — Password hashing
- `python-jose` (3.3.0) — JWT tokens
- `slowapi` (0.1.8) — Rate limiting
- `loguru` (0.7.0) — Logging
- `google-auth` (2.22.0) — Google OAuth

### 4. Configure Environment Variables

Create `.env` file in project root:

```env
# ===== Database =====
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=hypeon_mvp_db
MONGO_MAX_POOL_SIZE=100
MONGO_MIN_POOL_SIZE=10
MONGO_MAX_IDLE_TIME_MS=30000

# ===== JWT Authentication =====
JWT_SECRET=your-very-secure-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===== Frontend =====
FRONTEND_URL=http://localhost:3000

# ===== Email (Password Reset) =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=noreply@hypeon.ai

# ===== Google OAuth =====
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# ===== Environment =====
ENVIRONMENT=development
DEBUG=true
```

**Important Notes**:
- `JWT_SECRET` must be at least 32 characters
- Use random, secure values for production
- Don't commit `.env` to version control
- For Google OAuth, create credentials at [Google Cloud Console](https://console.cloud.google.com/)
- For Gmail SMTP, use [App Password](https://support.google.com/accounts/answer/185833), not regular password

### 5. Database Setup

#### Option A: Local MongoDB
1. Download from: https://www.mongodb.com/try/download/community
2. Install and start MongoDB service
3. Connection: `mongodb://localhost:27017/hypeon_mvp_db`

#### Option B: MongoDB Atlas (Cloud - Recommended for development)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account and cluster (M0 tier)
3. Create database user
4. Copy connection string to `MONGO_URI` in `.env`
5. Whitelist your IP in Network Access

#### Option C: Docker
```bash
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  --name mongodb mongo:latest
```

### 6. Start Backend

```bash
# Development with auto-reload (recommended)
uvicorn main:app --reload --port 8000

# For production
gunicorn main:app -w 4 -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker
```

### 7. Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/healthz
# Response: {"status": "ok"}

# Test database connection
curl http://localhost:8000/health/db
# Response: {"status": "ok", "message": "..."}

# Access API documentation
# Swagger: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 7. Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/healthz

# Should return:
{"status": "ok"}
```

## Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Using Postman
1. Import `Postman_Collection.json`
2. Configure environment variables
3. Start testing

### Using curl
```bash
# Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Pass123!"}'

# List products (with token)
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Backend won't start
```bash
# Port already in use
lsof -i :8000  # Find process
kill -9 <PID>   # Kill it

# Or use different port
uvicorn main:app --port 8001
```

### Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database connection failed
```bash
# Verify MongoDB is running
# Check MONGO_URI in .env
# Verify credentials if using Atlas
```

### 401 Unauthorized errors
- Check JWT_SECRET is set and consistent
- Verify token format: "Bearer <token>"
- Ensure token hasn't expired

## Development Workflow

```bash
# 1. Start backend with auto-reload
uvicorn main:app --reload

# 2. In another terminal, test
curl http://localhost:8000/health

# 3. Make changes - auto-reload happens
# 4. Test changes immediately

# 5. When done, press Ctrl+C to stop
```

## Production Deployment

Set environment variables:
```env
ENVIRONMENT=production
JWT_SECRET=<secure-key>
MONGO_URI=<production-uri>
FRONTEND_URL=<production-url>
```

Start with gunicorn:
```bash
gunicorn main:app -w 4 -b 0.0.0.0:8000
```

Or use Docker - see `Dockerfile` in project root.
