# Hypeon AI Backend

FastAPI backend for Hypeon AI MVP - A platform for discovering trending products and managing saved searches.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-supported-green.svg)](https://www.mongodb.com/)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- pip

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Backend-AIML-Hypeonai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start backend
uvicorn main:app --reload

# Verify it's running
curl http://localhost:8000/healthz
```

**Backend running at**: http://localhost:8000

**Interactive API Docs**: http://localhost:8000/docs

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[API Reference](docs/API.md)** | All 16 endpoints with examples |
| **[Setup Guide](docs/SETUP.md)** | Installation and configuration |
| **[Testing Guide](docs/TESTING.md)** | How to test with Swagger/Postman |
| **[Troubleshooting](docs/TROUBLESHOOTING.md)** | Common issues and solutions |
| **[Quick Reference](docs/QUICK_REFERENCE.md)** | Cheat sheet (print-friendly!) |

---

## ✨ Features

✅ **User Authentication**
- Email/password signup and login
- Google OAuth integration
- JWT token-based authentication
- Refresh token with httpOnly cookies
- Password reset via email
- Get current user profile

✅ **Product Management**
- List products with flexible filtering
- Filter by niche, platform, region
- Sort by hype score and growth metrics
- Full-text search capability
- Pagination support
- Get individual product details

✅ **Saved Searches**
- Save custom product search queries
- Manage search collections per user
- List all saved searches
- Retrieve specific saved searches
- Delete saved searches
- User-specific isolation (security)

✅ **Security**
- Rate limiting per endpoint type:
  - Auth endpoints: 5 requests/minute
  - Password reset: 3 requests/15 minutes
  - General: No global limit
- CORS protection with configurable origins
- Comprehensive security headers
- Password hashing with bcrypt
- JWT authentication with HS256
- HttpOnly cookies for refresh tokens

✅ **Developer Friendly**
- Interactive Swagger UI at `/docs`
- ReDoc documentation at `/redoc`
- Postman collection included
- Comprehensive API documentation
- Extensive error handling
- Structured logging with loguru
- Activity tracking for users

---

## 🏗️ Architecture

```
Backend-AIML-Hypeonai/
├── main.py                    # FastAPI application setup
├── requirements.txt           # Python 3.8+ dependencies
├── .env                       # Configuration (create this)
├── runtime.txt               # Python version
├── Dockerfile                # Docker containerization
├── Postman_Collection.json   # API collection
├── docs/                      # Documentation
│   ├── API.md                # Full API reference (v2.0)
│   ├── SETUP.md              # Installation & setup
│   ├── TESTING.md            # Testing guide
│   ├── INTEGRATION_GUIDE.md  # Frontend integration
│   ├── TROUBLESHOOTING.md    # Common issues
│   └── QUICK_REFERENCE.md    # Quick lookup
├── app/
│   ├── __init__.py
│   ├── deps.py               # Dependency injection
│   ├── schemas.py            # Pydantic models
│   ├── core/
│   │   ├── config.py         # Settings & configuration
│   │   └── events.py         # Startup/shutdown events
│   ├── routes/               # API endpoints
│   │   ├── auth.py           # Authentication (7 endpoints)
│   │   ├── products.py       # Products (2 endpoints)
│   │   └── saved_searches.py # Saved searches (4 endpoints)
│   ├── models/
│   │   └── user_model.py     # User database model
│   ├── middleware/           # Custom middleware
│   └── utils/
│       ├── security.py       # Password hashing, JWT tokens
│       ├── emailer.py        # Email sending
│       ├── logger.py         # Logging setup
│       ├── rate_limiter.py   # Rate limiting configuration
│       └── activity_tracker.py # User activity logging
└── README.md
```

---

## 📋 API Endpoints (17 Total)

### Health Checks (Public - 4 endpoints)
```
GET  /healthz                Basic health check
GET  /health                 Application health
GET  /health/db             Database health
GET  /health/full           Full system health
```

### Authentication (7 endpoints)
```
POST /api/auth/signup        Create account
POST /api/auth/login         User login
POST /api/auth/google        Google OAuth login
GET  /api/auth/me            Get current user
POST /api/auth/refresh       Refresh access token
POST /api/auth/logout        Logout user
POST /api/auth/forgot        Request password reset email
POST /api/auth/reset         Reset password with token
```

### Products - Auth Required (2 endpoints)
```
GET  /api/products/          List products (with filters)
GET  /api/products/{id}      Get product details
```

### Saved Searches - Auth Required (4 endpoints)
```
GET  /api/saved-searches/           List user's saved searches
POST /api/saved-searches/           Create saved search
GET  /api/saved-searches/{id}       Get specific search
DELETE /api/saved-searches/{id}     Delete search
```

See [API.md](docs/API.md) for detailed endpoint documentation with examples.

---

## 🔧 Configuration

### Environment Variables

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
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# ===== Environment =====
ENVIRONMENT=development
DEBUG=true
```

See [SETUP.md](docs/SETUP.md) for detailed configuration instructions.

---

## 🧪 Testing

### Option 1: Swagger UI (Best for beginners)
1. Start backend: `uvicorn main:app --reload`
2. Open: http://localhost:8000/docs
3. Click endpoint → "Try it out" → "Execute"

### Option 2: Postman (Professional)
1. Import: `Postman_Collection.json`
2. Configure environment variables
3. Start testing

### Option 3: curl (Command-line)
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Pass123!"}'
```

See [TESTING.md](docs/TESTING.md) for comprehensive testing guide.

---

## 🐛 Troubleshooting

**Backend won't start?** → See [SETUP.md](docs/SETUP.md#troubleshooting)

**API returns 401?** → Check authentication header format

**Database connection failed?** → Verify MongoDB is running and credentials are correct

**Rate limit exceeded?** → Wait or check rate limiting configuration

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

---

## 📊 Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| Auth | 5/min | 1 minute |
| Password Reset | 3/min | 15 minutes |
| General | 100/min | 1 minute |

---

## 🔐 Security

- ✅ JWT authentication with HS256
- ✅ Password hashing with bcrypt
- ✅ Rate limiting per endpoint
- ✅ CORS protection
- ✅ Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (MongoDB)
- ✅ XSS protection

---

## 🚀 Deployment

### Using Docker

```bash
# Build image
docker build -t hypeon-backend .

# Run container
docker run -p 8000:8000 \
  -e MONGO_URI=<uri> \
  -e JWT_SECRET=<secret> \
  hypeon-backend
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn main:app -w 4 -b 0.0.0.0:8000
```

See [SETUP.md](docs/SETUP.md) for production deployment guide.

---

## 📦 Dependencies

Main packages:
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **PyJWT** - JWT authentication
- **python-dotenv** - Environment variables
- **slowapi** - Rate limiting

Full list: See `requirements.txt`

---

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

---

## 📄 License

[Add your license here]

---

## 📞 Support

| Need | Resource |
|------|----------|
| API Questions | [API.md](docs/API.md) |
| Setup Help | [SETUP.md](docs/SETUP.md) |
| Testing Guide | [TESTING.md](docs/TESTING.md) |
| Troubleshooting | [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| Quick Lookup | [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) |

---

## 🔗 Links

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

**Created**: November 13, 2024  
**Version**: 1.0.0 (MVP)  
**Status**: Active Development

## Rate Limited Endpoints

- `POST /api/auth/signup` - 5 requests per minute
- `POST /api/auth/login` - 5 requests per minute
- `POST /api/auth/google` - 5 requests per minute
- `POST /api/auth/refresh` - 5 requests per minute
- `POST /api/auth/forgot` - 3 requests per hour
- `POST /api/auth/reset` - 3 requests per hour

# Hypeon AI Backend — Integration Guide

## 🚀 Base URLs

- **Development:** `http://localhost:8000`
- **Staging:** `https://hypeon-staging.onrender.com`
- **Production:** `https://hypeon-api.com`

---

## 🔐 Authentication Flow

### 1. Signup

**Endpoint:** `POST /api/auth/signup`

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Notes:**
- `refresh_token` is stored in httpOnly cookie (secure, not accessible to JS)
- `access_token` valid for 120 minutes
- Store `access_token` in memory (frontend)

---

### 2. Login

**Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** Same as signup

---

### 3. Google OAuth

**Endpoint:** `POST /api/auth/google`

**Request:**
```json
{
  "idToken": "<Google ID Token from frontend>"
}
```

**Response:** Same as signup

---

### 4. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Headers:**
```
Cookie: refresh_token=<refresh_token_from_cookie>
```

**Response:** New `access_token` and `refresh_token`

---

## 📦 Products Endpoint

### List Products

**Endpoint:** `GET /api/products/?niche=Wallpaper&limit=50&offset=0&sort=hypeScore:desc&q=best`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `niche` (string, optional) - Filter by niche
- `platform` (string, optional) - Filter by platform
- `region` (string, optional) - Filter by region
- `q` (string, optional) - Text search
- `limit` (int, default: 50) - Results per page
- `offset` (int, default: 0) - Pagination offset
- `sort` (string, default: hypeScore:desc) - Sort by field and direction

**Response:**
```json
{
  "total": 100,
  "limit": 50,
  "offset": 0,
  "returned": 50,
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Wallpaper A",
      "platform": "amazon",
      "niche": "Wallpaper",
      "region": "US",
      "hypeScore": 92,
      "growthWeekly": 5.2,
      "growthMonthly": 21.3,
      "metadata": {}
    }
  ]
}
```

---

### Get Single Product

**Endpoint:** `GET /api/products/{product_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Wallpaper A",
  "platform": "amazon",
  "niche": "Wallpaper",
  "region": "US",
  "hypeScore": 92,
  "growthWeekly": 5.2,
  "growthMonthly": 21.3,
  "metadata": {}
}
```

---

## 💾 Saved Searches

### List Saved Searches

**Endpoint:** `GET /api/saved-searches/`

**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "userId": "507f1f77bcf86cd799439012",
    "name": "My Search",
    "params": {
      "niche": "Wallpaper",
      "region": "US"
    },
    "createdAt": "2024-01-15T10:30:00Z",
    "resultSnapshot": [...]
  }
]
```

### Create Saved Search

**Endpoint:** `POST /api/saved-searches/`

**Request:**
```json
{
  "name": "My Wallpaper Search",
  "params": {
    "niche": "Wallpaper",
    "region": "US"
  },
  "notes": "Search for trending wallpapers"
}
```

---

## 🛑 Rate Limiting

- **Auth endpoints:** 5 requests/minute
- **Password reset:** 3 requests/hour

**Error Response (429):**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 🧪 Frontend .env Example

```
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=923334824395-4l0ii8019adnnvl38nu1ips5sp3pklf6.apps.googleusercontent.com
```

---

## ✅ Health Check

Monitor backend status:

```bash
curl https://hypeon-api.com/health/full
```

---

## 🐛 Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized (invalid/expired token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (e.g., email already exists) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |
