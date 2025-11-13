# Quick Reference

**Print this page for your desk!**

---

## 🚀 Quick Start Commands

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
uvicorn main:app --reload

# Test
curl http://localhost:8000/healthz
```

---

## 📍 All Endpoints

### Health (Public)
```
GET  /healthz              Basic health
GET  /health               App health
GET  /health/db            Database health
GET  /health/full          Full status
```

### Auth
```
POST /api/auth/signup           Create account
POST /api/auth/login            Login
POST /api/auth/google           Google OAuth
GET  /api/auth/me               Get current user
POST /api/auth/refresh          Refresh token
POST /api/auth/logout           Logout
POST /api/auth/forgot           Request password reset
POST /api/auth/reset            Reset password (from email)
```

### Products (🔒 Auth Required)
```
GET  /api/products/        List products
GET  /api/products/{id}    Get product details
```

### Saved Searches (🔒 Auth Required)
```
GET  /api/saved-searches/           List searches
POST /api/saved-searches/           Create search
GET  /api/saved-searches/{id}       Get search
DELETE /api/saved-searches/{id}     Delete search
```

---

## 🔐 Authentication

```
Authorization: Bearer <access_token>
```

**Token Info**:
- Access: Expires in 120 min
- Refresh: Expires in 7 days
- Format: JWT (HS256)

---

## 📝 Common Requests

### Sign Up
```json
POST /api/auth/signup
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

### Login
```json
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

### Get Current User
```
GET /api/auth/me
Header: Authorization: Bearer <access_token>
```

### Refresh Token
```
POST /api/auth/refresh
Cookie: refresh_token=<refresh_token>
```

### Request Password Reset
```json
POST /api/auth/forgot
{
  "email": "john@example.com"
}
```

### List Products
```
GET /api/products/?niche=electronics&limit=10&sort=hypeScore:desc
Header: Authorization: Bearer <access_token>
```

### Get Product Details
```
GET /api/products/{product_id}
Header: Authorization: Bearer <access_token>
```

### Create Saved Search
```json
POST /api/saved-searches/
{
  "name": "My Search",
  "params": {"niche": "electronics", "platform": "amazon"},
  "notes": "Optional notes"
}
```

### List Saved Searches
```
GET /api/saved-searches/
Header: Authorization: Bearer <access_token>
```

### Delete Saved Search
```
DELETE /api/saved-searches/{id}
Header: Authorization: Bearer <access_token>
```

---

## ✅ Status Codes

| Code | Meaning |
|------|---------|
| 200 | ✅ OK |
| 201 | ✅ Created |
| 400 | ❌ Bad Request |
| 401 | ❌ Unauthorized |
| 403 | ❌ Forbidden |
| 404 | ❌ Not Found |
| 409 | ❌ Conflict |
| 429 | ❌ Rate Limited |
| 500 | ❌ Server Error |
| 503 | ❌ Service Down |

---

## ⏱️ Rate Limits

```
Auth endpoints:      5/min
Password reset:      3/15min
General endpoints:   100/min

Returns: 429 Too Many Requests
```

---

## 🔧 Query Parameters

### Products Endpoint
```
/api/products/
?niche=electronics         Filter by niche
?platform=amazon           Filter by platform
?region=US                 Filter by region
?limit=20                  Max results (default: 50)
?offset=0                  Skip N items
?sort=hypeScore:desc       Sort order
?q=laptop                  Text search
```

---

## 🌐 URLs

| Purpose | URL |
|---------|-----|
| **API** | http://localhost:8000 |
| **Swagger** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |

---

## 🔒 Environment Variables

```env
MONGO_URI=mongodb+srv://...
MONGO_DB=hypeon_mvp_db
JWT_SECRET=your-secret-key
GOOGLE_CLIENT_ID=your-id
SMTP_HOST=smtp.gmail.com
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

---

## 🗄️ Database Schema

### Users
```json
{
  "_id": ObjectId,
  "name": string,
  "email": string,
  "passwordHash": string,
  "googleId": string (optional),
  "createdAt": datetime,
  "lastLoginAt": datetime
}
```

### Products
```json
{
  "_id": ObjectId,
  "title": string,
  "platform": string,
  "niche": string,
  "hypeScore": number,
  "growthWeekly": number,
  "growthMonthly": number
}
```

### Saved Searches
```json
{
  "_id": ObjectId,
  "userId": ObjectId,
  "name": string,
  "params": object,
  "createdAt": datetime,
  "resultSnapshot": array
}
```

---

## 🐛 Quick Debugging

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token, add Bearer prefix |
| 404 Not Found | Verify endpoint path |
| 429 Too Many Requests | Wait or reduce rate |
| 500 Server Error | Check logs, verify .env |
| CORS Error | Add frontend URL to whitelist |

---

## 📦 Tools

| Tool | URL | Best For |
|------|-----|----------|
| Swagger UI | /docs | Learning |
| Postman | Import JSON | Professional testing |
| curl | Command line | Scripting |
| ReDoc | /redoc | Reading |

---

## 🧪 Testing Workflow

```
1. Start backend
   uvicorn main:app --reload

2. Open Swagger or Postman
   http://localhost:8000/docs

3. Sign up
   POST /api/auth/signup

4. Copy access_token

5. Test other endpoints
   Use token in Authorization header

6. Verify responses
   Check status codes and data
```

---

## 💡 Pro Tips

1. Keep token in Postman environment variable
2. Use test scripts for auto token saving
3. Check logs first when debugging
4. Test with curl before Postman if having issues
5. Health check is fastest test
6. Print this page for reference
7. QUICK_REFERENCE.md is always here

---

## 🎯 Test Cases

Must pass:
```
✓ GET /healthz returns 200
✓ POST /api/auth/signup returns token
✓ GET /api/products/ with token succeeds
✓ POST /api/saved-searches/ creates search
✓ GET /api/saved-searches/ lists searches
✓ DELETE removes search
✓ Invalid credentials return 401
```

---

## 🔍 Response Format

### Success
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {"id": "...", "email": "..."}
}
```

### Error
```json
{
  "detail": "Error description"
}
```

---

## 📞 Help Resources

| Need | File |
|------|------|
| Setup | SETUP.md |
| Testing | TESTING.md |
| Errors | TROUBLESHOOTING.md |
| Full API | API.md |

---

## ✨ Keyboard Shortcuts

```
Postman:
  Ctrl+K        Search endpoints
  Ctrl+Alt+C    Open console
  Ctrl+Enter    Send request

Swagger:
  Ctrl+F        Find endpoint
  Spacebar      Try it out
```

---

## 🎓 Common Workflows

### Authenticate & Test
```
1. POST /api/auth/signup
2. Copy access_token
3. Add to Authorization header
4. GET /api/products/
```

### Save & Retrieve
```
1. Authenticate
2. POST /api/saved-searches/
3. Note ID
4. GET /api/saved-searches/{id}
```

### Search Products
```
GET /api/products/
?niche=electronics
&limit=10
&sort=hypeScore:desc
```

---

## 🚀 Go Live Checklist

- [ ] Backend starts without errors
- [ ] All 16 endpoints accessible
- [ ] Authentication working
- [ ] Database connected
- [ ] Health checks passing
- [ ] Rate limiting working
- [ ] CORS configured
- [ ] Errors handled properly
- [ ] Tokens expiring correctly
- [ ] Logs showing normally

---

**📌 Pin this file to your desk!**

Last updated: November 13, 2024
