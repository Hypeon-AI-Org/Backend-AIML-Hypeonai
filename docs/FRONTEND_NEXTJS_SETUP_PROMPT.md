# NEXT.JS FRONTEND - INTEGRATION SETUP PROMPT

**For: AI Coding Agent**  
**Framework**: Next.js 13+  
**Backend API**: FastAPI at http://localhost:8000  
**Status**: Integration needed  
**Created**: November 13, 2025  

---

## YOUR TASK

You are tasked with setting up and fixing the Next.js frontend to integrate with the Hypeon AI Backend API.

**DO NOT deviate from this prompt.**  
**Follow every step exactly as specified.**

---

## STEP 1: PROJECT INFORMATION

Your frontend project is located at:
```
C:\Users\umarf\Desktop\Code_base\Hypeon-Frontend
```

**Backend API Details:**
- **Base URL**: http://localhost:8000
- **Repository**: Backend-AIML-Hypeonai (MVP_Backend branch)
- **Status**: ✅ Running and ready
- **Documentation**: C:\Users\umarf\Desktop\Code_base\Backend-AIML-Hypeonai\docs\

---

## STEP 2: OPEN YOUR WORKSPACE

1. Open a new VS Code window
2. Open folder: `C:\Users\umarf\Desktop\Code_base\Hypeon-Frontend`
3. Open terminal in VS Code (Ctrl+`)

---

## STEP 3: VERIFY PROJECT STRUCTURE

Check your project structure:

```bash
# Run this command
dir /s /b | findstr /E "\.(ts|tsx|js|json)$" | head -50
```

**You should have:**
- `package.json` ✅
- `next.config.js` or `next.config.ts` ✅
- `src/` or `app/` folder ✅
- `tsconfig.json` ✅

If missing, initialize Next.js:
```bash
npx create-next-app@latest . --typescript --tailwind --eslint
```

---

## STEP 4: INSTALL REQUIRED DEPENDENCIES

Run these commands in terminal:

```bash
npm install axios@1.6.2
npm install typescript@latest
npm install @types/node --save-dev
npm install @types/react --save-dev
```

Verify installation:
```bash
npm list axios
```

---

## STEP 5: CREATE API CLIENT STRUCTURE

Create these folders:

```bash
# From project root
mkdir -p src/lib/api
mkdir -p src/lib/types
mkdir -p src/lib/utils
mkdir -p src/hooks
```

---

## STEP 6: CREATE ENVIRONMENT CONFIGURATION FILE

Create file: `.env.local`

**EXACT content:**

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=10000

# Google OAuth (if using)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here

# Feature Flags
NEXT_PUBLIC_ENABLE_GOOGLE_LOGIN=true
NEXT_PUBLIC_ENABLE_DEBUG_MODE=true

# URLs
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

---

## STEP 7: CREATE API CLIENT FILE

Create file: `src/lib/api/client.ts`

**EXACT CODE:**

```typescript
import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000');

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // CRITICAL: Allow cookies
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = typeof window !== 'undefined' 
          ? localStorage.getItem('access_token')
          : null;
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // Handle 401 - Token expired
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const response = await axios.post(
              `${API_BASE_URL}/api/auth/refresh`,
              {},
              { withCredentials: true }
            );

            const { access_token } = response.data;
            if (typeof window !== 'undefined') {
              localStorage.setItem('access_token', access_token);
            }

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed - redirect to login
            if (typeof window !== 'undefined') {
              localStorage.removeItem('access_token');
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  get<T = any>(url: string, config?: any) {
    return this.client.get<T>(url, config);
  }

  post<T = any>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config);
  }

  put<T = any>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config);
  }

  delete<T = any>(url: string, config?: any) {
    return this.client.delete<T>(url, config);
  }
}

export const apiClient = new ApiClient();
```

---

## STEP 8: CREATE TYPE DEFINITIONS

Create file: `src/lib/types/api.types.ts`

**EXACT CODE:**

```typescript
// ===== AUTH =====
export interface AuthUser {
  id: string;
  name: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: AuthUser;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

// ===== PRODUCTS =====
export interface Product {
  id: string;
  title: string;
  platform: string;
  niche: string;
  region: string;
  hypeScore: number;
  growthWeekly: number;
  growthMonthly: number;
  metadata?: Record<string, any>;
}

export interface ProductFilters {
  niche?: string;
  platform?: string;
  region?: string;
  limit?: number;
  offset?: number;
  sort?: string;
  q?: string;
}

export interface ProductsListResponse {
  total: number;
  limit: number;
  offset: number;
  returned: number;
  items: Product[];
}

// ===== SAVED SEARCHES =====
export interface SavedSearchParams {
  niche?: string;
  platform?: string;
  region?: string;
  limit?: number;
  offset?: number;
  sort?: string;
  q?: string;
}

export interface SavedSearch {
  id: string;
  userId: string;
  name: string;
  params: SavedSearchParams;
  notes?: string;
  resultSnapshot: any[];
  createdAt: string;
}

export interface CreateSavedSearchRequest {
  name: string;
  params: SavedSearchParams;
  notes?: string;
  snapshot?: any[];
}

// ===== ERROR =====
export interface ApiErrorResponse {
  detail: string;
}
```

---

## STEP 9: CREATE AUTH API CLIENT

Create file: `src/lib/api/auth.ts`

**EXACT CODE:**

```typescript
import { apiClient } from './client';
import {
  AuthResponse,
  SignupRequest,
  LoginRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  AuthUser,
} from '../types/api.types';

export const authApi = {
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/signup', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', data);
    return response.data;
  },

  googleLogin: async (idToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/google', {
      idToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<AuthUser> => {
    const response = await apiClient.get<AuthUser>('/api/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/refresh', {});
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout', {});
  },

  forgotPassword: async (data: ForgotPasswordRequest): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      '/api/auth/forgot',
      data
    );
    return response.data;
  },

  resetPassword: async (data: ResetPasswordRequest): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      '/api/auth/reset',
      data
    );
    return response.data;
  },
};
```

---

## STEP 10: CREATE PRODUCTS API CLIENT

Create file: `src/lib/api/products.ts`

**EXACT CODE:**

```typescript
import { apiClient } from './client';
import {
  Product,
  ProductFilters,
  ProductsListResponse,
} from '../types/api.types';

export const productsApi = {
  listProducts: async (filters?: ProductFilters): Promise<ProductsListResponse> => {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const url = `/api/products/${params.toString() ? '?' + params.toString() : ''}`;
    const response = await apiClient.get<ProductsListResponse>(url);
    return response.data;
  },

  getProduct: async (productId: string): Promise<Product> => {
    const response = await apiClient.get<Product>(`/api/products/${productId}`);
    return response.data;
  },
};
```

---

## STEP 11: CREATE SAVED SEARCHES API CLIENT

Create file: `src/lib/api/saved-searches.ts`

**EXACT CODE:**

```typescript
import { apiClient } from './client';
import {
  SavedSearch,
  CreateSavedSearchRequest,
} from '../types/api.types';

export const savedSearchesApi = {
  list: async (): Promise<SavedSearch[]> => {
    const response = await apiClient.get<SavedSearch[]>('/api/saved-searches/');
    return response.data;
  },

  create: async (data: CreateSavedSearchRequest): Promise<SavedSearch> => {
    const response = await apiClient.post<SavedSearch>(
      '/api/saved-searches/',
      data
    );
    return response.data;
  },

  get: async (id: string): Promise<SavedSearch> => {
    const response = await apiClient.get<SavedSearch>(`/api/saved-searches/${id}`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/saved-searches/${id}`);
  },
};
```

---

## STEP 12: CREATE AUTH HOOK

Create file: `src/hooks/useAuth.ts`

**EXACT CODE:**

```typescript
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { AuthUser } from '@/lib/types/api.types';

export const useAuth = () => {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const currentUser = await authApi.getCurrentUser();
          setUser(currentUser);
        }
      } catch (err: any) {
        console.error('Failed to load user:', err);
        localStorage.removeItem('access_token');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await authApi.login({ email, password });
        localStorage.setItem('access_token', response.access_token);
        setUser(response.user);
        router.push('/products');
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Login failed';
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  const signup = useCallback(
    async (name: string, email: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await authApi.signup({ name, email, password });
        localStorage.setItem('access_token', response.access_token);
        setUser(response.user);
        router.push('/products');
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Signup failed';
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authApi.logout();
      localStorage.removeItem('access_token');
      setUser(null);
      router.push('/login');
    } catch (err: any) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  }, [router]);

  return { user, loading, error, login, signup, logout };
};
```

---

## STEP 13: UPDATE NEXT.JS CONFIGURATION

Update file: `next.config.js` or `next.config.ts`

**REQUIRED:**

```typescript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    NEXT_PUBLIC_API_TIMEOUT: process.env.NEXT_PUBLIC_API_TIMEOUT,
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/:path*`,
        },
      ],
    };
  },
};

module.exports = nextConfig;
```

---

## STEP 14: TEST THE INTEGRATION

Run these commands in terminal:

```bash
# 1. Start Next.js dev server
npm run dev

# 2. In another terminal, test health endpoint
curl http://localhost:8000/healthz

# 3. Open browser to http://localhost:3000
# 4. Check browser console for errors (F12)
```

**You should see:**
- ✅ No CORS errors
- ✅ No connection refused errors
- ✅ Page loads without errors
- ✅ Console shows API calls being made

---

## STEP 15: CREATE A TEST LOGIN PAGE

If you don't have a login page, create file: `src/app/login/page.tsx`

**MINIMAL CODE:**

```typescript
'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}
```

---

## STEP 16: CREATE A TEST PRODUCTS PAGE

If you don't have products page, create file: `src/app/products/page.tsx`

**MINIMAL CODE:**

```typescript
'use client';

import { useState, useEffect } from 'react';
import { productsApi } from '@/lib/api/products';
import { Product } from '@/lib/types/api.types';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await productsApi.listProducts({
          limit: 10,
          sort: 'hypeScore:desc',
        });
        setProducts(response.items);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch products');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h1>Products</h1>
      <div>
        {products.length === 0 ? (
          <p>No products found</p>
        ) : (
          products.map((product) => (
            <div key={product.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
              <h3>{product.title}</h3>
              <p>Hype Score: {product.hypeScore}</p>
              <p>Weekly Growth: {product.growthWeekly}%</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

---

## STEP 17: VERIFY INTEGRATION WORKS

**Checklist - All must be ✅ BEFORE moving forward:**

```
☐ npm install completed without errors
☐ .env.local file created with API_BASE_URL
☐ src/lib/api/client.ts created
☐ src/lib/api/auth.ts created
☐ src/lib/api/products.ts created
☐ src/lib/api/saved-searches.ts created
☐ src/lib/types/api.types.ts created
☐ src/hooks/useAuth.ts created
☐ next.config.js/ts updated
☐ npm run dev starts without errors
☐ Browser loads http://localhost:3000 without errors
☐ F12 Console shows NO errors
☐ Can see API calls in Network tab
☐ Authorization header present in requests
☐ Login attempt receives response from backend
☐ 401 errors trigger token refresh
☐ CORS headers present in responses
```

---

## STEP 18: FIX ANY REMAINING ISSUES

**If you see errors, provide:**

1. **Error message** (full console output)
2. **File path** where error occurs
3. **Screenshot** of the error
4. **Network tab** showing failed request

Then I can provide specific fixes.

---

## COMMON ISSUES & FIXES

### Issue: "Module not found" for api/client

**Fix:**
```bash
# Verify path exists
ls -la src/lib/api/

# If not, create it
mkdir -p src/lib/api
mkdir -p src/lib/types
```

---

### Issue: CORS errors in console

**Fix:**
Ensure `.env.local` has:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

### Issue: "Cannot find module 'axios'"

**Fix:**
```bash
npm install axios@1.6.2
```

---

### Issue: 401 errors on every request

**Fix:**
1. Make sure token is stored: `localStorage.setItem('access_token', token)`
2. Check token format in DevTools → Application → LocalStorage
3. Should be: `eyJhbGc...` (no "Bearer" prefix)

---

### Issue: Backend connection refused

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/healthz

# If fails, start backend
cd C:\Users\umarf\Desktop\Code_base\Backend-AIML-Hypeonai
uvicorn main:app --reload
```

---

## STEP 19: RUN FINAL TESTS

```bash
# Test 1: Signup (should work)
# Test 2: Login (should work)
# Test 3: Fetch products (should work)
# Test 4: Create saved search (should work)
# Test 5: List saved searches (should work)
# Test 6: Delete saved search (should work)
# Test 7: Logout (should work)
```

---

## NEXT STEPS AFTER INTEGRATION

Once integration is complete:

1. ✅ Build complete pages (signup, products, saved searches)
2. ✅ Add error boundaries
3. ✅ Add loading states
4. ✅ Add form validation
5. ✅ Add TypeScript strict mode
6. ✅ Test with production API URL
7. ✅ Deploy to production

---

## SUCCESS CRITERIA

**Your frontend is successfully integrated when:**

✅ You can signup/login without errors  
✅ Access token stored in localStorage  
✅ API calls include Authorization header  
✅ Products page loads with data  
✅ Saved searches CRUD works  
✅ Token automatically refreshes on 401  
✅ Logout clears all data  
✅ No CORS errors in console  
✅ All Network requests show 200/201/204 status  
✅ No "Cannot GET" errors  

---

## SUPPORT

If you get stuck:

1. **Check the error message carefully** - copy/paste it exactly
2. **Check file paths** - ensure all files in correct location
3. **Check .env.local** - ensure API_BASE_URL is set
4. **Check terminal** - ensure both backend and frontend running
5. **Check DevTools** - look at Network and Console tabs

**Always check backend first:**
```bash
curl http://localhost:8000/health/full
```

---

**Document Version**: 1.0  
**Status**: Ready to execute  
**Last Updated**: November 13, 2025  
**For**: Next.js Frontend Coding Agent
