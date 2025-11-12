# API Reference

**API Base URL**: `http://localhost:8000` or `https://<deployed-url>`

**Interactive Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## Health Check Endpoints

### Basic Health Check
```http
GET /healthz
```
Returns: `{"status": "ok"}`

### Application Health
```http
GET /health
```
Returns: `{"status": "healthy", "service": "Hypeon AI Backend"}`

### Database Health
```http
GET /health/db
```
Returns database connectivity status.

### Full Health Check
```http
GET /health/full
```
Returns: Complete health status with database and environment info.

---

## Authentication Endpoints

All authenticated endpoints require: `Authorization: Bearer <access_token>`

### Sign Up
```http
POST /api/auth/signup
```
**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```
**Response**: `{"access_token": "...", "refresh_token": "...", "user": {...}, "token_type": "bearer"}`

### Login
```http
POST /api/auth/login
```
**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```
**Response**: Same as signup

### Google OAuth Login
```http
POST /api/auth/google
```
**Request**:
```json
{
  "idToken": "google_id_token_here"
}
```

### Refresh Token
```http
POST /api/auth/refresh
```
Gets new access token using refresh token from cookie.

### Logout
```http
POST /api/auth/logout
```
Clears refresh token cookie.

### Forgot Password
```http
POST /api/auth/forgot
```
**Request**:
```json
{
  "email": "john@example.com"
}
```
Sends password reset email.

### Reset Password
```http
POST /api/auth/reset
```
**Request**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewPassword123!"
}
```

---

## Product Endpoints

### List Products
```http
GET /api/products/
```
**Query Parameters**:
- `niche` (optional): Filter by niche
- `platform` (optional): Filter by platform
- `region` (optional): Filter by region
- `limit` (default: 50): Max results
- `offset` (default: 0): Pagination offset
- `sort` (default: "hypeScore:desc"): Sort field and direction
- `q` (optional): Text search query

**Example**: `/api/products/?niche=electronics&limit=20&sort=hypeScore:desc`

**Response**:
```json
{
  "total": 150,
  "limit": 20,
  "offset": 0,
  "returned": 20,
  "items": [...]
}
```

### Get Product Details
```http
GET /api/products/{product_id}
```
Returns detailed product information.

---

## Saved Search Endpoints

### List Saved Searches
```http
GET /api/saved-searches/
```
Lists all saved searches for current user.

### Create Saved Search
```http
POST /api/saved-searches/
```
**Request**:
```json
{
  "name": "Search Name",
  "params": {
    "niche": "electronics",
    "platform": "amazon"
  },
  "notes": "Optional notes"
}
```

### Get Saved Search
```http
GET /api/saved-searches/{id}
```
Returns specific saved search.

### Delete Saved Search
```http
DELETE /api/saved-searches/{id}
```
Deletes a saved search.

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK / Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 429 | Too Many Requests (Rate Limited) |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Authentication

**JWT Bearer Token**: Use in header for all protected endpoints
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Expiration**:
- Access Token: 120 minutes (default)
- Refresh Token: 7 days (default)

---

## Rate Limiting

| Endpoint Type | Limit | Window |
|---|---|---|
| Authentication | 5/min | 1 minute |
| Password Reset | 3/min | 15 minutes |
| General | 100/min | 1 minute |

Returns `429 Too Many Requests` when exceeded.

---

## Error Response Format

```json
{
  "detail": "Error description"
}
```

---

## CORS Policy

Allowed Origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- Frontend URL (if set via `FRONTEND_URL` env var)

**Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS
**Allowed Headers**: Content-Type, Authorization

---

## Security Headers

All responses include:
- `X-Content-Type-Options`: nosniff
- `X-Frame-Options`: DENY
- `X-XSS-Protection`: 1; mode=block
- `Strict-Transport-Security`: max-age=31536000
- `Referrer-Policy`: strict-origin-when-cross-origin
- `Content-Security-Policy`: default-src 'self'
