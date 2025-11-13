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
  "password": "SecurePassword123!"
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

### 3. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Request:**
```
Cookie: refresh_token=<refresh_token_from_httpOnly_cookie>
```

**Response (200):**
```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<new_refresh_token>",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "token_type": "bearer"
}
```

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

### 4. Get Current User

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com"
}
```

---

### 5. Logout

**Endpoint:** `POST /api/auth/logout`

**Response (200):**
```json
{ "message": "Logged out successfully" }
```

**Frontend Implementation:**
```typescript
const logout = async () => {
  await fetch('http://localhost:8000/api/auth/logout', {
    method: 'POST',
    credentials: 'include'
  });
  
  localStorage.removeItem('access_token');
  window.location.href = '/login';
};
```

---

### 6. Forgot Password

**Endpoint:** `POST /api/auth/forgot`

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response (200):**
```json
{
  "message": "If an account exists, an email was sent"
}
```

**Rate Limited:** 3 requests per 15 minutes

**Frontend Implementation:**
```typescript
const requestPasswordReset = async (email: string) => {
  const response = await fetch('http://localhost:8000/api/auth/forgot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  
  if (response.ok) {
    // Show success message - don't reveal if email exists
    showNotification('Check your email for reset instructions');
  }
};
```

---

### 7. Reset Password

**Endpoint:** `POST /api/auth/reset`

**Request:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewPassword123!"
}
```

**Response (200):**
```json
{ "message": "Password updated" }
```

**Rate Limited:** 3 requests per 15 minutes

**Frontend Implementation:**
```typescript
const resetPassword = async (token: string, newPassword: string) => {
  const response = await fetch('http://localhost:8000/api/auth/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword })
  });
  
  if (response.ok) {
    showNotification('Password reset successfully');
    window.location.href = '/login';
  } else {
    const error = await response.json();
    showError(error.detail);
  }
};
```

---

## 📦 Products Endpoint

All product endpoints require authentication.

### List Products (with Filters & Search)

**Endpoint:** `GET /api/products/`

**Query Parameters**:
- `niche` (optional): Filter by product niche
- `platform` (optional): Filter by platform (e.g., 'amazon', 'shopify')
- `region` (optional): Filter by region
- `limit` (default: 50, max: 100): Results per page
- `offset` (default: 0): Pagination offset
- `sort` (default: "hypeScore:desc"): Sort field and direction (format: "field:direction")
- `q` (optional): Full-text search query

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/products/?niche=electronics&platform=amazon&region=US&limit=20&sort=hypeScore:desc" \
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
      "title": "Wireless Bluetooth Headphones",
      "platform": "amazon",
      "niche": "electronics",
      "region": "US",
      "hypeScore": 92,
      "growthWeekly": 5.2,
      "growthMonthly": 21.3,
      "metadata": {}
    }
  ]
}
```

**Frontend Implementation:**
```typescript
const fetchProducts = async (filters: {
  niche?: string;
  platform?: string;
  region?: string;
  limit?: number;
  offset?: number;
  q?: string;
  sort?: string;
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
  
  if (!response.ok) throw new Error('Failed to fetch products');
  return response.json();
};
```

---

### Get Single Product

**Endpoint:** `GET /api/products/{product_id}`

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Wireless Bluetooth Headphones",
  "platform": "amazon",
  "niche": "electronics",
  "region": "US",
  "hypeScore": 92,
  "growthWeekly": 5.2,
  "growthMonthly": 21.3,
  "metadata": {}
}
```

---

## 💾 Saved Searches

All saved search endpoints require authentication.

### List User's Saved Searches

**Endpoint:** `GET /api/saved-searches/`

**Response (200):**
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "userId": "507f1f77bcf86cd799439011",
    "name": "Premium Electronics",
    "params": {
      "niche": "electronics",
      "region": "US",
      "platform": "amazon"
    },
    "notes": "Search for trending electronics",
    "resultSnapshot": [],
    "createdAt": "2024-01-10T15:30:00Z"
  }
]
```

---

### Create Saved Search

**Endpoint:** `POST /api/saved-searches/`

**Request:**
```json
{
  "name": "Premium Electronics",
  "params": {
    "niche": "electronics",
    "region": "US",
    "platform": "amazon",
    "limit": 50
  },
  "notes": "Search for trending electronics",
  "snapshot": []
}
```

**Response (201):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "userId": "507f1f77bcf86cd799439011",
  "name": "Premium Electronics",
  "params": { "niche": "electronics", "region": "US", "platform": "amazon", "limit": 50 },
  "notes": "Search for trending electronics",
  "resultSnapshot": [],
  "createdAt": "2024-01-10T15:30:00Z"
}
```

**Frontend Implementation:**
```typescript
const createSavedSearch = async (searchData: {
  name: string;
  params: Record<string, any>;
  notes?: string;
  snapshot?: any[];
}) => {
  const response = await fetch(
    'http://localhost:8000/api/saved-searches/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(searchData)
    }
  );
  
  if (!response.ok) throw new Error('Failed to create saved search');
  return response.json();
};
```

---

### Get Saved Search

**Endpoint:** `GET /api/saved-searches/{search_id}`

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439012",
  "userId": "507f1f77bcf86cd799439011",
  "name": "Premium Electronics",
  "params": { "niche": "electronics", "region": "US" },
  "notes": "Search notes",
  "resultSnapshot": [],
  "createdAt": "2024-01-10T15:30:00Z"
}
```

---

### Delete Saved Search

**Endpoint:** `DELETE /api/saved-searches/{search_id}`

**Response (204):** Empty response body

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
Content-Security-Policy: default-src 'self'
```

---

## 🚫 Error Handling

### Standard Error Response

```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Codes

| Code | Scenario |
|------|----------|
| **400** | Bad Request / Invalid data |
| **401** | Unauthorized / Missing token |
| **403** | Forbidden / Not authorized |
| **404** | Not Found / Resource doesn't exist |
| **409** | Conflict / Email already exists |
| **422** | Validation Error |
| **429** | Rate Limit Exceeded |
| **500** | Server Error |

**Rate Limiting:**
- Auth endpoints: 5 requests/minute
- Password reset: 3 requests/15 minutes
- Other endpoints: No limit (per user activity tracking)

---

## 📝 Frontend .env Configuration

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here

# Feature Flags
VITE_ENABLE_GOOGLE_LOGIN=true
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
