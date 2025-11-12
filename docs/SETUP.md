# Setup & Installation

## Prerequisites

- Python 3.8+
- MongoDB (local, cloud, or Docker)
- Git
- pip (Python package manager)

## Environment Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Backend-AIML-Hypeonai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in project root:

```env
# Database
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=hypeon_mvp_db
MONGO_MAX_POOL_SIZE=100
MONGO_MIN_POOL_SIZE=10

# JWT
JWT_SECRET=your-very-secure-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend
FRONTEND_URL=http://localhost:3000

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=noreply@hypeon.ai

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Environment
ENVIRONMENT=development
```

### 5. Database Setup

#### Option A: Local MongoDB
1. Download from: https://www.mongodb.com/try/download/community
2. Install following wizard
3. Start MongoDB service
4. Connection: `mongodb://localhost:27017/`

#### Option B: MongoDB Atlas (Cloud)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create account and cluster
3. Create database user
4. Get connection string
5. Whitelist your IP

#### Option C: Docker
```bash
docker run -d \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  --name mongodb \
  mongo:latest
```

Connection: `mongodb://admin:password@localhost:27017/`

### 6. Start Backend

```bash
# Development with auto-reload
uvicorn main:app --reload --port 8000

# Or using Python directly
python main.py
```

**Expected output**:
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
