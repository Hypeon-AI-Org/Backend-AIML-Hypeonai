# Troubleshooting

## Common Setup Issues

### Backend Won't Start

**Error**: "Address already in use"
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (Windows)
taskkill /PID <PID> /F

# Or use different port
uvicorn main:app --port 8001
```

**Error**: "ModuleNotFoundError: No module named..."
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

**Error**: "Could not connect to MongoDB"
```bash
# Check MongoDB is running
# Verify MONGO_URI in .env
# Check credentials if using Atlas
# Verify IP is whitelisted (Atlas)
```

---

## Database Connection Issues

### MongoDB Connection Refused
```
Problem: Connection timeout
Solution:
  1. Verify MongoDB is running
  2. Check MONGO_URI format
  3. Test with mongosh: mongosh "mongodb://localhost:27017"
```

### Authentication Failed (Atlas)
```
Problem: "authentication failed"
Solution:
  1. Verify username and password
  2. Check @ in password is URL encoded
  3. Verify IP is whitelisted
  4. Ensure user has database access
```

### Connection Pool Errors
```
Problem: "Connection pool is closed"
Solution:
  1. Restart backend
  2. Check MONGO_MAX_POOL_SIZE in .env
  3. Verify database isn't full
```

---

## Authentication Errors

### 401 Unauthorized - Invalid Token
```
Solution:
  1. Copy full token (including all dots)
  2. Use format: "Authorization: Bearer <token>"
  3. Check token hasn't expired
  4. Get new token via /api/auth/login
  5. Check JWT_SECRET is same on server
```

### 401 Unauthorized - Token Not Found
```
Solution:
  1. Ensure Authorization header is present
  2. In Postman: Check "Bearer Token" is selected
  3. In curl: Include -H "Authorization: Bearer..."
  4. Cookie-based: Check browser sends cookies
```

### 403 Forbidden - Not Authorized
```
Solution:
  1. Verify you own the resource
  2. Check user_id matches
  3. For saved searches: Use own searches only
  4. For products: No ownership restrictions
```

---

## Testing Issues

### Postman: Can't Import Collection
```
Solution:
  1. Verify JSON file is valid
  2. Try "Import from text"
  3. Paste JSON content directly
  4. Check file isn't corrupted
```

### Postman: Authorization Not Working
```
Solution:
  1. Type must be "Bearer Token"
  2. Token field must have value
  3. Token automatically added to headers
  4. Check Authorization tab, not Headers
```

### Postman: Variables Not Substituting
```
Solution:
  1. Select correct environment (top-right)
  2. Variable syntax: {{variable_name}}
  3. Verify variable exists in environment
  4. Refresh environment if changed
```

### Swagger: Can't Authorize
```
Solution:
  1. Click lock icon (🔒)
  2. Select "HTTPBearer"
  3. Paste full token (with scheme prefix)
  4. Click "Authorize"
  5. Close dialog
```

---

## Rate Limiting Issues

### 429 Too Many Requests
```
Solution:
  1. Wait for rate limit window to reset
  2. Auth endpoints: 5/min
  3. Password reset: 3/15min
  4. General: 100/min
  5. Implement exponential backoff
```

### Rate Limit Not Resetting
```
Solution:
  1. Wait full window duration
  2. Use different IP/environment
  3. Check rate limiter configuration
  4. Restart backend if stuck
```

---

## API Response Issues

### 404 Not Found
```
Solution:
  1. Verify endpoint path is correct
  2. Check resource ID exists
  3. Try endpoint without path parameters
  4. Verify HTTP method (GET vs POST)
```

### 422 Unprocessable Entity
```
Solution:
  1. Check request body JSON is valid
  2. Verify all required fields present
  3. Check field data types match schema
  4. See error message for specific issue
```

### 409 Conflict
```
Solution:
  1. Usually "Email already in use"
  2. Try with different email
  3. Check database for duplicates
  4. For other: Check unique constraints
```

### 500 Internal Server Error
```
Solution:
  1. Check backend terminal logs
  2. Verify .env variables are set
  3. Check database connection
  4. Try restarting backend
  5. Check request is valid JSON
```

---

## CORS Errors

### Browser: "CORS error"
```
Solution:
  1. Check FRONTEND_URL in .env
  2. Add your URL to cors_origins in main.py
  3. Restart backend
  4. Clear browser cache (Ctrl+Shift+Delete)
  5. Test in Postman first (Postman bypasses CORS)
```

### Preflight Request Fails
```
Solution:
  1. Ensure OPTIONS method is allowed
  2. Check Access-Control headers
  3. Try from different origin
  4. Verify Content-Type header
```

---

## Email/Password Reset Issues

### Password Reset Email Not Received
```
Solution:
  1. Check SMTP settings in .env
  2. Verify email service is configured
  3. Check spam/junk folder
  4. Test with simple email first
  5. Check SMTP_PASS is correct (app password for Gmail)
```

### Password Reset Token Invalid
```
Solution:
  1. Token expires in 1 hour
  2. Request new reset email
  3. Check token isn't modified
  4. Verify email matches request
```

---

## Performance Issues

### Slow Response Times
```
Solution:
  1. Check backend logs for database queries
  2. Verify database indexes are created
  3. Monitor CPU and memory usage
  4. Check network latency
  5. Profile with timing data
```

### High Database Latency
```
Solution:
  1. Check database performance
  2. Review slow query logs
  3. Verify connection pool size
  4. Check database load
  5. Consider caching
```

---

## Environment Variable Issues

### "Undefined Environment Variable"
```
Solution:
  1. Create .env file in project root
  2. Ensure file is in same directory as main.py
  3. Check variable name matches exactly
  4. Restart backend after changing .env
  5. Use: python-dotenv for loading
```

### Variables Not Loading
```
Solution:
  1. File must be named exactly ".env"
  2. Format: KEY=value (no spaces)
  3. No quotes needed (unless in value)
  4. Comments start with #
  5. Restart Python after changes
```

---

## Security Issues

### Token Leaked/Exposed
```
Solution:
  1. Change JWT_SECRET immediately
  2. Invalidate all existing tokens
  3. Users need to re-login
  4. Check logs for misuse
  5. Store secrets in secure vault
```

### HTTPS Certificate Issues
```
Solution:
  1. Generate self-signed cert for dev
  2. Use proper cert for production
  3. Check certificate expiration
  4. Update browser trusted stores
```

---

## Quick Diagnostic

Run this to check everything:

```bash
# 1. Health checks
curl http://localhost:8000/healthz
curl http://localhost:8000/health/db

# 2. Can create user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Pass123!"}'

# 3. Can list products
# (use token from step 2)
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <token>"
```

If all 3 work: ✅ Everything is functional!

---

## Still Need Help?

1. Check terminal logs for error details
2. Review .env configuration
3. Verify database is connected
4. Try with Postman (bypass Swagger issues)
5. Restart backend and database
6. Check GitHub issues or documentation
