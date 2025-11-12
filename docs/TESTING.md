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
   ↓ Get tokens
2. GET /api/products/
   ↓ Browse products
3. POST /api/saved-searches/
   ↓ Save a search
4. GET /api/saved-searches/{id}
   ↓ View saved search
5. DELETE /api/saved-searches/{id}
   ↓ Delete search
6. POST /api/auth/logout
   ↓ Logout
```

### Scenario 2: Error Handling
Test these should fail:
```
- POST /api/auth/signup (duplicate email) → 409 Conflict
- POST /api/auth/login (wrong password) → 401 Unauthorized
- GET /api/products/ (no token) → 401 Unauthorized
- POST /api/saved-searches (invalid data) → 422 Unprocessable Entity
```

### Scenario 3: Authentication Flow
```
1. Login → Get tokens
2. Use access_token in Authorization header
3. When expired: POST /api/auth/refresh
4. Get new access_token
5. Continue using API
```

### Scenario 4: Product Search
```
1. GET /api/products/ (no filters)
2. GET /api/products/?niche=electronics
3. GET /api/products/?niche=electronics&limit=10&sort=hypeScore:desc
4. GET /api/products/?q=laptop (text search)
5. Verify correct results
```

### Scenario 5: Saved Searches
```
1. Create saved search
2. List saved searches
3. Get specific search
4. Verify ownership (only own searches visible)
5. Delete search
6. Verify deleted (404 on GET)
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
