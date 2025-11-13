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
**Response (201)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "token_type": "bearer"
}
```
**Status Codes**:
- `201 Created` — User successfully registered
- `400 Bad Request` — Invalid email or weak password
- `409 Conflict` — Email already registered
- `429 Too Many Requests` — Rate limited

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
**Response (200)**: Same structure as signup
**Status Codes**:
- `200 OK` — Login successful
- `401 Unauthorized` — Invalid credentials
- `404 Not Found` — User does not exist
- `429 Too Many Requests` — Rate limited

### Google OAuth Login
```http
POST /api/auth/google
```
**Request**:
```json
{
  "idToken": "google_id_token_from_frontend"
}
```
**Response (201/200)**:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": { "id": "...", "name": "...", "email": "..." },
  "token_type": "bearer"
}
```
**Status Codes**:
- `201 Created` — New user created via Google OAuth
- `200 OK` — Existing user logged in
- `400 Bad Request` — Invalid Google token
- `500 Internal Server Error` — Google auth error

### Get Current User
```http
GET /api/auth/me
```
**Response (200)**:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com"
}
```
**Status Codes**:
- `200 OK` — User found
- `401 Unauthorized` — Not authenticated

### Refresh Token
```http
POST /api/auth/refresh
```
**Description**: Gets new access token using refresh token from httpOnly cookie.

**Response (200)**:
```json
{
  "access_token": "new_token...",
  "refresh_token": "new_refresh_token...",
  "user": { "id": "...", "name": "...", "email": "..." },
  "token_type": "bearer"
}
```
**Status Codes**:
- `200 OK` — Token refreshed
- `401 Unauthorized` — Invalid or missing refresh token

### Logout
```http
POST /api/auth/logout
```
**Response (200)**:
```json
{
  "message": "Logged out successfully"
}
```
Clears refresh token httpOnly cookie and invalidates session.

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
**Response (200)**:
```json
{
  "message": "If an account exists, an email was sent"
}
```
**Notes**: Always returns success message to prevent user enumeration. Password reset link valid for 1 hour.
**Status Codes**:
- `200 OK` — Request processed
- `429 Too Many Requests` — Rate limited (3/15min)

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
**Response (200)**:
```json
{
  "message": "Password updated"
}
```
**Status Codes**:
- `200 OK` — Password reset successful
- `400 Bad Request` — Invalid or expired token
- `500 Internal Server Error` — Database error
- `429 Too Many Requests` — Rate limited (3/15min)

---

## Product Endpoints

All product endpoints require authentication.

### List Products
```http
GET /api/products/
```
**Query Parameters**:
- `niche` (optional): Filter by product niche
- `platform` (optional): Filter by platform (e.g., 'amazon', 'shopify')
- `region` (optional): Filter by region
- `limit` (default: 50): Max results to return
- `offset` (default: 0): Pagination offset
- `sort` (default: "hypeScore:desc"): Sort field and direction (format: "field:direction")
- `q` (optional): Full-text search query

**Example**: `/api/products/?niche=electronics&platform=amazon&limit=20&sort=hypeScore:desc`

**Response (200)**:
```json
{
  "total": 150,
  "limit": 20,
  "offset": 0,
  "returned": 20,
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Product Name",
      "platform": "amazon",
      "niche": "electronics",
      "region": "US",
      "hypeScore": 8.5,
      "growthWeekly": 15.3,
      "growthMonthly": 42.1,
      "metadata": {}
    }
  ]
}
```
**Status Codes**:
- `200 OK` — Products retrieved
- `401 Unauthorized` — Not authenticated
- `500 Internal Server Error` — Database error

### Get Product Details
```http
GET /api/products/{product_id}
```
**Path Parameters**:
- `product_id` (required): MongoDB ObjectId of the product

**Response (200)**:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Product Name",
  "platform": "amazon",
  "niche": "electronics",
  "region": "US",
  "hypeScore": 8.5,
  "growthWeekly": 15.3,
  "growthMonthly": 42.1,
  "metadata": {}
}
```
**Status Codes**:
- `200 OK` — Product found
- `401 Unauthorized` — Not authenticated
- `404 Not Found` — Product does not exist

---

## Saved Search Endpoints

All saved search endpoints require authentication.

### List Saved Searches
```http
GET /api/saved-searches/
```
**Response (200)**:
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "userId": "507f1f77bcf86cd799439011",
    "name": "My Search",
    "params": {
      "niche": "electronics",
      "platform": "amazon"
    },
    "notes": "Optional notes",
    "resultSnapshot": [],
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
```
**Status Codes**:
- `200 OK` — Searches retrieved
- `401 Unauthorized` — Not authenticated
- `500 Internal Server Error` — Database error

### Create Saved Search
```http
POST /api/saved-searches/
```
**Request**:
```json
{
  "name": "My Search",
  "params": {
    "niche": "electronics",
    "platform": "amazon",
    "limit": 50
  },
  "notes": "Search for trending electronics",
  "snapshot": []
}
```

**Response (201)**:
```json
{
  "id": "507f1f77bcf86cd799439012",
  "userId": "507f1f77bcf86cd799439011",
  "name": "My Search",
  "params": { "niche": "electronics", "platform": "amazon", "limit": 50 },
  "notes": "Search for trending electronics",
  "resultSnapshot": [],
  "createdAt": "2024-01-15T10:30:00Z"
}
```
**Status Codes**:
- `201 Created` — Saved search created
- `400 Bad Request` — Invalid request data
- `401 Unauthorized` — Not authenticated
- `500 Internal Server Error` — Database error

### Get Saved Search
```http
GET /api/saved-searches/{id}
```
**Path Parameters**:
- `id` (required): Saved search ID

**Response (200)**:
```json
{
  "id": "507f1f77bcf86cd799439012",
  "userId": "507f1f77bcf86cd799439011",
  "name": "My Search",
  "params": { "niche": "electronics" },
  "notes": "Search notes",
  "resultSnapshot": [],
  "createdAt": "2024-01-15T10:30:00Z"
}
```
**Status Codes**:
- `200 OK` — Search found
- `401 Unauthorized` — Not authenticated
- `403 Forbidden` — Not authorized to view this search
- `404 Not Found` — Saved search does not exist

### Delete Saved Search
```http
DELETE /api/saved-searches/{id}
```
**Path Parameters**:
- `id` (required): Saved search ID

**Response (204)**:
Empty response body.

**Status Codes**:
- `204 No Content` — Search deleted successfully
- `401 Unauthorized` — Not authenticated
- `403 Forbidden` — Not authorized to delete this search
- `404 Not Found` — Saved search does not exist

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
