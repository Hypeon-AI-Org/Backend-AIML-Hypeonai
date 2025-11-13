# Testing Guide

## Quick Start

### Option 1: Swagger UI (Easiest)
1. Start backend: `uvicorn main:app --reload`
2. Open: http://localhost:8000/docs
3. Click any endpoint → "Try it out" → "Execute"

### Option 2: Postman (Professional)
1. Import: `Postman_Collection.json`
2. Set environment variables
3. Start testing

### Option 3: curl (Scripting)
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Pass123!"}'
```

---

## Testing with Swagger UI

### 1. Sign Up
- Go to `/docs`
- Find `POST /api/auth/signup`
- Click "Try it out"
- Enter credentials:
  ```json
  {
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPassword123!"
  }
  ```
- Click "Execute"
- Copy `access_token` from response

### 2. Authorize
- Click lock icon (🔒) at top right
- Select "HTTPBearer"
- Paste access token
- Click "Authorize"

### 3. Test Other Endpoints
- All protected endpoints now use your token
- Try GET `/api/products/`
- Try POST `/api/saved-searches/`

---

## Testing with Postman

### Import Collection
1. Open Postman
2. Click "Import" (top-left)
3. Select `Postman_Collection.json`
4. Collection appears in left sidebar

### Configure Environment
1. Click "Environments" (left sidebar)
2. Create new: "Hypeon Development"
3. Add variables:

```
base_url: http://localhost:8000
access_token: (empty - will auto-fill)
refresh_token: (empty)
email: test@example.com
password: TestPassword123!
```

### Run Test Scenario

**Step 1: Sign Up**
- Go to Auth → Sign Up
- Click "Send"
- Tokens auto-saved to environment

**Step 2: List Products**
- Go to Products → List Products
- Click "Send"
- Response shows products

**Step 3: Create Saved Search**
- Go to Saved Searches → Create
- Click "Send"
- Search created

**Step 4: List Saved Searches**
- Go to Saved Searches → List
- Click "Send"
- Shows your searches

---

## Test Scenarios

### Scenario 1: Complete User Journey
```
1. POST /api/auth/signup
   ↓ Get access_token and refresh_token
2. GET /api/auth/me
   ↓ Verify user info
3. GET /api/products/
   ↓ Browse products
4. POST /api/saved-searches/
   ↓ Save a search
5. GET /api/saved-searches/
   ↓ List saved searches
6. GET /api/saved-searches/{id}
   ↓ View specific saved search
7. DELETE /api/saved-searches/{id}
   ↓ Delete search
8. POST /api/auth/logout
   ↓ Logout
```

### Scenario 2: Error Handling
Test these error scenarios:
```
- POST /api/auth/signup (duplicate email) → 409 Conflict
- POST /api/auth/login (wrong password) → 401 Unauthorized
- POST /api/auth/login (non-existent user) → 401 Unauthorized
- GET /api/products/ (no token) → 401 Unauthorized
- GET /api/saved-searches/{invalid-id} → 404 Not Found
- DELETE /api/saved-searches/{other-user-id} → 403 Forbidden
```

### Scenario 3: Authentication Flow
```
1. POST /api/auth/login → Get tokens
2. Use access_token in Authorization header
3. Make API call with access_token
4. When expired: POST /api/auth/refresh
5. Get new access_token
6. Continue using API with new token
```

### Scenario 4: Product Search and Filtering
```
1. GET /api/products/ (no filters) → List all products
2. GET /api/products/?niche=electronics → Filter by niche
3. GET /api/products/?platform=amazon&region=US → Filter by platform and region
4. GET /api/products/?limit=10&sort=hypeScore:desc → Limit and sort
5. GET /api/products/?q=laptop → Full-text search
6. GET /api/products/{product_id} → Get specific product
```

### Scenario 5: Saved Searches Management
```
1. POST /api/saved-searches/ → Create search
2. GET /api/saved-searches/ → List all searches
3. GET /api/saved-searches/{id} → Get specific search
4. Verify user can only see own searches
5. DELETE /api/saved-searches/{id} → Delete search
```

### Scenario 6: Password Reset Flow
```
1. POST /api/auth/forgot → Request password reset
2. Extract reset token from email (simulated or check logs)
3. POST /api/auth/reset → Reset password with token
4. POST /api/auth/login → Login with new password
```

### Scenario 7: Google OAuth
```
1. Get Google ID token from frontend
2. POST /api/auth/google → Login/register with Google token
3. Verify user created if new
4. Verify existing user logs in
```

### Scenario 8: Rate Limiting
```
1. POST /api/auth/signup → First request (success)
2. POST /api/auth/signup → Rapid repeat requests
3. Verify 429 Too Many Requests after 5 requests/min
4. Wait 1 minute and verify access restored
```

---

## Debugging Tips

### 1. Check Backend Logs
Look at terminal where backend is running:
- `INFO` logs: Normal operations
- `WARNING` logs: Potential issues
- `ERROR` logs: Problems to investigate

### 2. Use Postman Console
- Press Ctrl+Alt+C (Cmd+Option+C on Mac)
- View request/response details
- See headers and body

### 3. Verify Environment
```bash
# Test health
curl http://localhost:8000/health

# Test database
curl http://localhost:8000/health/db

# Check full status
curl http://localhost:8000/health/full
```

### 4. Common Issues

**"401 Unauthorized"**
- Check token is copied completely
- Verify Authorization header format: `Bearer <token>`
- Get new token if expired

**"404 Not Found"**
- Verify endpoint path is correct
- Check resource ID exists
- Try without parameters first

**"429 Too Many Requests"**
- Wait for rate limit window (1-15 minutes)
- Reduce request frequency

**"500 Internal Server Error"**
- Check server logs
- Verify .env variables
- Restart backend

---

## Using Test Scripts in Postman

### Auto-Save Tokens

Add to "Tests" tab of login/signup request:

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set('access_token', jsonData.access_token);
    pm.environment.set('refresh_token', jsonData.refresh_token);
    console.log('Tokens saved!');
}
```

### Validate Response

```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has access_token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access_token');
});
```

---

## Performance Testing

### Response Time Benchmarks

| Endpoint | Expected | Alert |
|----------|----------|-------|
| Health checks | < 50ms | > 200ms |
| Auth endpoints | < 300ms | > 1000ms |
| Product list | < 500ms | > 2000ms |
| Saved searches | < 400ms | > 1500ms |

### Measure in Postman

Response time shown in bottom right after request.

---

## Rate Limiting

### Limits
- Auth endpoints: 5/min
- Password reset: 3/15min
- General: 100/min

### Testing Rate Limit
```bash
# Send 6 rapid requests
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d "{...}"
done

# 6th request returns 429
```

---

## Test Data

### Test Account
```
Email: test@example.com
Password: TestPassword123!
```

### Test Product ID
Use any ID from `GET /api/products/` response

### Test Search Parameters
```json
{
  "niche": "electronics",
  "platform": "amazon",
  "minHypeScore": 80
}
```

---

## Postman Environment Variables

Keep these in your environment:

```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "refresh_token": "",
  "user_id": "",
  "saved_search_id": "",
  "email": "test@example.com",
  "password": "TestPassword123!"
}
```

Use variables in requests: `{{base_url}}/api/products/`

---

## Next Steps

1. ✅ Complete all test scenarios
2. ✅ Verify response times are acceptable
3. ✅ Test error cases
4. ✅ Understand rate limiting
5. ✅ Share Postman collection with team

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick lookup.
