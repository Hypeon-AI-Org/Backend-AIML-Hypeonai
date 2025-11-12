# Hypeon AI Backend — Frontend Integration Guide

## 🚀 Environment Setup

### Base URLs

- **Local Development:** `http://localhost:8000`
- **Staging (Render):** `https://hypeon-staging.onrender.com`
- **Production:** `https://hypeon-api.com`

### API Documentation

- **Swagger UI:** `{BASE_URL}/docs`
- **ReDoc:** `{BASE_URL}/redoc`
- **OpenAPI Schema:** `{BASE_URL}/openapi.json`

---

## 🔐 Authentication System

### Overview

The authentication system uses **JWT tokens** with refresh token rotation:
- **Access Token:** Short-lived (120 minutes), stored in memory
- **Refresh Token:** Long-lived (7 days), stored in httpOnly cookie
- **Token Type:** Bearer tokens in Authorization header

### 1. User Signup

**Endpoint:** `POST /api/auth/signup`

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "confirmPassword": "SecurePassword123!"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request` — Invalid email format or weak password
- `409 Conflict` — Email already registered

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*)

---

### 2. User Login

**Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):** Same structure as signup

**Error Responses:**
- `401 Unauthorized` — Invalid credentials
- `404 Not Found` — User does not exist

---

### 3. Google OAuth Login

**Endpoint:** `POST /api/auth/google`

**Request:**
```json
{
  "idToken": "<Google ID Token from frontend>"
}
```

**Getting Google ID Token (Frontend):**
```javascript
// Using @react-oauth/google
import { GoogleLogin } from '@react-oauth/google';

<GoogleLogin
  onSuccess={credentialResponse => {
    const idToken = credentialResponse.credential;
    // Send idToken to backend
    fetch('http://localhost:8000/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idToken }),
      credentials: 'include'
    })
  }}
/>
```

**Response (200):** Same structure as signup

---

### 4. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Request:**
```
Headers:
  Cookie: refresh_token=<refresh_token_from_httpOnly_cookie>
```

**Response (200):**
```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<new_refresh_token>",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid or expired refresh token

**Frontend Implementation:**
```typescript
// Automatically refresh token when it expires
const refreshAccessToken = async () => {
  const response = await fetch('http://localhost:8000/api/auth/refresh', {
    method: 'POST',
    credentials: 'include' // Important: send cookies
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
  } else {
    // Redirect to login
    window.location.href = '/login';
  }
};
```

---

### 5. Logout

**Endpoint:** `POST /api/auth/logout`

**Request:**
```
Headers:
  Authorization: Bearer <access_token>
```

**Response (200):**
```json
{ "message": "Logged out successfully" }
```

**Frontend Implementation:**
```typescript
const logout = async () => {
  await fetch('http://localhost:8000/api/auth/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    credentials: 'include'
  });
  
  localStorage.removeItem('access_token');
  window.location.href = '/login';
};
```

---

### 6. Password Reset

**Step 1: Request Password Reset**

**Endpoint:** `POST /api/auth/forgot-password`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{ "message": "Password reset email sent" }
```

**Rate Limited:** 3 requests per hour

**Step 2: Reset Password**

**Endpoint:** `POST /api/auth/reset-password`

**Request:**
```json
{
  "token": "<reset_token_from_email_link>",
  "newPassword": "NewSecurePassword123!",
  "confirmPassword": "NewSecurePassword123!"
}
```

**Response (200):**
```json
{ "message": "Password reset successfully" }
```

---

## 📦 Products Endpoint

### List Products (with Filters & Search)

**Endpoint:** `GET /api/products/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Query Parameters:**

| Parameter | Type | Default | Example | Description |
|-----------|------|---------|---------|-------------|
| `niche` | string | - | `Wallpaper` | Filter by product niche |
| `platform` | string | - | `amazon` | Filter by platform (amazon, etsy, etc.) |
| `region` | string | - | `US` | Filter by region (US, UK, EU, etc.) |
| `q` | string | - | `trending` | Full-text search across title and description |
| `minHype` | number | 0 | `75` | Minimum hype score (0-100) |
| `maxHype` | number | 100 | `95` | Maximum hype score (0-100) |
| `sortBy` | string | `hypeScore` | `growthMonthly` | Sort field |
| `order` | string | `desc` | `asc` | Sort order (asc/desc) |
| `limit` | integer | 50 | `25` | Results per page (max 100) |
| `offset` | integer | 0 | `50` | Pagination offset |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/products/?niche=Wallpaper&region=US&minHype=75&limit=20" \
  -H "Authorization: Bearer <access_token>"
```

**Response (200):**
```json
{
  "total": 150,
  "limit": 20,
  "offset": 0,
  "returned": 20,
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Modern Minimalist Wallpaper",
      "description": "High-quality, trendy wallpaper perfect for offices",
      "platform": "amazon",
      "niche": "Wallpaper",
      "region": "US",
      "hypeScore": 92,
      "growthWeekly": 5.2,
      "growthMonthly": 21.3,
      "growthYearly": 156.8,
      "averageRating": 4.8,
      "reviewCount": 1250,
      "price": 29.99,
      "url": "https://amazon.com/...",
      "imageUrl": "https://cdn.example.com/...",
      "lastUpdated": "2024-01-15T10:30:00Z",
      "metadata": {
        "trending": true,
        "bestseller": true,
        "newRelease": false
      }
    }
  ]
}
```

**Frontend Implementation:**
```typescript
const fetchProducts = async (filters: {
  niche?: string;
  region?: string;
  minHype?: number;
  limit?: number;
  offset?: number;
}) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) params.append(key, String(value));
  });
  
  const response = await fetch(
    `http://localhost:8000/api/products/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    }
  );
  
  return response.json();
};
```

---

### Get Single Product

**Endpoint:** `GET /api/products/{product_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Modern Minimalist Wallpaper",
  "description": "High-quality, trendy wallpaper perfect for offices",
  "platform": "amazon",
  "niche": "Wallpaper",
  "region": "US",
  "hypeScore": 92,
  "growthWeekly": 5.2,
  "growthMonthly": 21.3,
  "growthYearly": 156.8,
  "averageRating": 4.8,
  "reviewCount": 1250,
  "price": 29.99,
  "url": "https://amazon.com/...",
  "imageUrl": "https://cdn.example.com/...",
  "lastUpdated": "2024-01-15T10:30:00Z",
  "metadata": { "trending": true }
}
```

**Error Responses:**
- `404 Not Found` — Product does not exist
- `401 Unauthorized` — Missing or invalid access token

---

## 💾 Saved Searches

### List User's Saved Searches

**Endpoint:** `GET /api/saved-searches/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "userId": "507f1f77bcf86cd799439011",
    "name": "Premium US Wallpapers",
    "description": "High-hype, trending wallpapers in the US market",
    "filters": {
      "niche": "Wallpaper",
      "region": "US",
      "minHype": 80,
      "sortBy": "hypeScore",
      "order": "desc"
    },
    "resultCount": 45,
    "resultSnapshot": [
      { "id": "...", "title": "...", "hypeScore": 92 }
    ],
    "createdAt": "2024-01-10T15:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z",
    "lastRun": "2024-01-15T10:30:00Z"
  }
]
```

---

### Create Saved Search

**Endpoint:** `POST /api/saved-searches/`

**Request:**
```json
{
  "name": "Premium US Wallpapers",
  "description": "High-hype, trending wallpapers in the US market",
  "filters": {
    "niche": "Wallpaper",
    "region": "US",
    "minHype": 80,
    "sortBy": "hypeScore"
  }
}
```

**Response (201):** Same as list response item

---

### Update Saved Search

**Endpoint:** `PUT /api/saved-searches/{search_id}`

**Request:** Same as create (all fields optional)

**Response (200):** Updated search object

---

### Delete Saved Search

**Endpoint:** `DELETE /api/saved-searches/{search_id}`

**Response (200):**
```json
{ "message": "Saved search deleted successfully" }
```

---

### Get Search Results

**Endpoint:** `GET /api/saved-searches/{search_id}/results`

**Response (200):**
```json
{
  "searchId": "507f1f77bcf86cd799439012",
  "searchName": "Premium US Wallpapers",
  "total": 45,
  "limit": 50,
  "offset": 0,
  "items": [...]
}
```

---

## 🛡️ Headers & Authentication

### Required Headers (All Protected Routes)

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Response Headers (Always Present)

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
Content-Security-Policy: default-src 'self'; ...
```

---

## 🚫 Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "status": 400,
  "message": "Additional context (dev mode only)"
}
```

### Common Error Codes

| Code | Scenario | Example |
|------|----------|---------|
| **400** | Bad Request | Invalid query parameters, malformed JSON |
| **401** | Unauthorized | Missing or expired access token |
| **403** | Forbidden | Insufficient permissions (rate limited) |
| **404** | Not Found | Resource does not exist |
| **409** | Conflict | Email already registered |
| **422** | Validation Error | Invalid request body |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Server Error | Unexpected error (logged server-side) |

**Rate Limiting:**
- Auth endpoints: 5 requests/minute
- Password reset: 3 requests/hour
- Other endpoints: 60 requests/minute

---

## 📝 Frontend .env Configuration

Create `.env.local` in your React project:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=923334824395-4l0ii8019adnnvl38nu1ips5sp3pklf6.apps.googleusercontent.com

# Feature Flags
VITE_ENABLE_GOOGLE_LOGIN=true
VITE_ENABLE_EMAIL_VERIFICATION=true

# Analytics
VITE_SENTRY_DSN=https://...@sentry.io/...
```

---

## 🧪 Local Testing Checklist

- [ ] Backend running: `uvicorn main:app --reload`
- [ ] `/docs` loads Swagger UI
- [ ] `/health` returns `200 OK`
- [ ] `/health/full` shows database connected
- [ ] Signup endpoint works
- [ ] Login endpoint returns access token
- [ ] Protected endpoint with valid token returns 200
- [ ] Protected endpoint without token returns 401
- [ ] CORS headers present for localhost:3000
- [ ] No console errors or warnings

---

## 🚀 Deployment URLs

Once deployed on Render:

- **API Base:** `https://hypeon-api.onrender.com`
- **API Docs:** `https://hypeon-api.onrender.com/docs`
- **Health Check:** `https://hypeon-api.onrender.com/health`

Update your frontend `.env` to point to production URL once deployed.

---

## 📞 Support & Debugging

### View Backend Logs

```bash
# Render dashboard: Settings → Logs
```

### Local Debug Mode

```bash
ENVIRONMENT=development uvicorn main:app --reload
# Shows detailed error messages (don't use in production)
```

### Check Database Connection

```bash
curl http://localhost:8000/health/db
```

### Monitor API Performance

```bash
curl http://localhost:8000/health/full
```
