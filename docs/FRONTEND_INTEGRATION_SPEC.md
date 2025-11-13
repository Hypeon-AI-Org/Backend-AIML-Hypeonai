# FRONTEND INTEGRATION SPECIFICATION

**Status**: Production Ready  
**Last Updated**: November 13, 2025  
**Backend Version**: v1.0  
**Required Backend Port**: 8000  

---

## TABLE OF CONTENTS

1. [Setup & Configuration](#setup--configuration)
2. [Environment Variables](#environment-variables)
3. [API Base URL Configuration](#api-base-url-configuration)
4. [Authentication System](#authentication-system)
5. [HTTP Interceptor Setup](#http-interceptor-setup)
6. [Component Implementation Guide](#component-implementation-guide)
7. [State Management](#state-management)
8. [Error Handling](#error-handling)
9. [Response Type Definitions](#response-type-definitions)
10. [Testing Checklist](#testing-checklist)
11. [Deployment Checklist](#deployment-checklist)

---

## SETUP & CONFIGURATION

### 1.1 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts           # HTTP client with interceptors
│   │   ├── auth.ts             # Auth API endpoints
│   │   ├── products.ts         # Products API endpoints
│   │   └── saved-searches.ts   # Saved searches API endpoints
│   ├── hooks/
│   │   ├── useAuth.ts          # Auth hook
│   │   ├── useProducts.ts      # Products hook
│   │   └── useSavedSearches.ts # Saved searches hook
│   ├── store/                  # State management (Redux/Zustand)
│   │   ├── auth.store.ts
│   │   ├── products.store.ts
│   │   └── searches.store.ts
│   ├── types/
│   │   ├── api.types.ts        # API response types
│   │   ├── auth.types.ts       # Auth types
│   │   └── product.types.ts    # Product types
│   ├── utils/
│   │   ├── storage.ts          # LocalStorage helpers
│   │   └── validators.ts       # Input validators
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Signup.tsx
│   │   ├── Products.tsx
│   │   ├── SavedSearches.tsx
│   │   └── Profile.tsx
│   └── App.tsx
├── .env.local                  # Local environment variables
└── package.json
```

### 1.2 Dependencies to Install

```bash
# Core dependencies (EXACT versions for compatibility)
npm install axios@1.6.2
npm install react-router-dom@6.x
npm install typescript@5.x

# For state management (choose ONE)
npm install zustand@4.x  # OR
npm install redux@4.x redux-react@8.x

# For Google OAuth
npm install @react-oauth/google@0.12.1

# Testing
npm install vitest@1.x
npm install @testing-library/react@14.x

# Additional utilities
npm install date-fns@2.x
npm install lodash-es@4.x
```

### 1.3 HTTP Client Setup

Create `src/api/client.ts`:

```typescript
import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 10000;

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // CRITICAL: Allow cookies (refresh token)
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
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
            // Attempt token refresh
            const response = await axios.post(
              `${API_BASE_URL}/api/auth/refresh`,
              {},
              { withCredentials: true }
            );

            const { access_token } = response.data;
            localStorage.setItem('access_token', access_token);

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh failed - redirect to login
            localStorage.removeItem('access_token');
            window.location.href = '/login';
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

## ENVIRONMENT VARIABLES

### 2.1 .env.local (Development)

**EXACT format - Do NOT deviate:**

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here

# Feature Flags
VITE_ENABLE_GOOGLE_LOGIN=true
VITE_ENABLE_EMAIL_VERIFICATION=false
VITE_ENABLE_DEBUG_MODE=true

# Deployment URLs
VITE_FRONTEND_URL=http://localhost:3000
```

### 2.2 .env.production

```env
# API Configuration
VITE_API_BASE_URL=https://your-production-api-url.com
VITE_API_TIMEOUT=15000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=production-google-client-id

# Feature Flags
VITE_ENABLE_GOOGLE_LOGIN=true
VITE_ENABLE_EMAIL_VERIFICATION=true
VITE_ENABLE_DEBUG_MODE=false

# Deployment URLs
VITE_FRONTEND_URL=https://your-production-frontend-url.com
```

### 2.3 Environment Variables in Vite

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env': {},
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
});
```

---

## API BASE URL CONFIGURATION

### 3.1 Conditional Base URL

The API base URL MUST respect these rules:

```typescript
// src/config/api.ts
export const API_CONFIG = {
  // Development
  development: {
    baseURL: 'http://localhost:8000',
    timeout: 10000,
  },
  // Staging
  staging: {
    baseURL: 'https://staging-api.hypeon.com',
    timeout: 15000,
  },
  // Production
  production: {
    baseURL: 'https://api.hypeon.com',
    timeout: 15000,
  },
};

// Determine environment
const env = import.meta.env.MODE || 'development';
export const API_BASE_URL = API_CONFIG[env as keyof typeof API_CONFIG].baseURL;
export const API_TIMEOUT = API_CONFIG[env as keyof typeof API_CONFIG].timeout;
```

### 3.2 CORS Headers Expected

These headers MUST be present in responses:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 600
```

If not present, check backend CORS configuration.

---

## AUTHENTICATION SYSTEM

### 4.1 Auth Flow Diagram

```
┌─────────────┐
│   Signup    │
│   /signup   │
└──────┬──────┘
       │ POST {name, email, password}
       ▼
┌─────────────────────────────┐
│ Backend validates & creates │
│ User, generates tokens      │
└──────┬──────────────────────┘
       │ Response: {access_token, refresh_token, user}
       ▼
┌──────────────────────────────────┐
│ Store access_token in localStorage│
│ Store refresh_token in cookie    │
│ (handled by withCredentials)      │
└──────────────────────────────────┘
```

### 4.2 Login Implementation

**EXACT implementation required:**

```typescript
// src/api/auth.ts
import { apiClient } from './client';

interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: {
    id: string;
    name: string;
    email: string;
  };
}

export const authApi = {
  // Signup
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      '/api/auth/signup',
      data
    );
    return response.data;
  },

  // Login
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      '/api/auth/login',
      data
    );
    return response.data;
  },

  // Google OAuth
  googleLogin: async (idToken: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      '/api/auth/google',
      { idToken }
    );
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<{
    id: string;
    name: string;
    email: string;
  }> => {
    const response = await apiClient.get(
      '/api/auth/me'
    );
    return response.data;
  },

  // Refresh token
  refreshToken: async (): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>(
      '/api/auth/refresh',
      {}
    );
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout');
  },

  // Request password reset
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const response = await apiClient.post(
      '/api/auth/forgot',
      { email }
    );
    return response.data;
  },

  // Reset password
  resetPassword: async (
    token: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    const response = await apiClient.post(
      '/api/auth/reset',
      { token, new_password: newPassword }
    );
    return response.data;
  },
};
```

### 4.3 Login Component

```typescript
// src/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await authApi.login({ email, password });
      
      // Store token
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // Redirect
      navigate('/products');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### 4.4 Google OAuth Setup

```typescript
// src/pages/GoogleLogin.tsx
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { authApi } from '../api/auth';
import { useNavigate } from 'react-router-dom';

export const GoogleLoginComponent: React.FC = () => {
  const navigate = useNavigate();

  const handleGoogleLogin = async (credentialResponse: CredentialResponse) => {
    try {
      const response = await authApi.googleLogin(credentialResponse.credential);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      navigate('/products');
    } catch (error) {
      console.error('Google login failed:', error);
    }
  };

  return (
    <GoogleLogin
      onSuccess={handleGoogleLogin}
      onError={() => console.log('Login Failed')}
    />
  );
};
```

### 4.5 Signup Component

```typescript
// src/pages/Signup.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';

export const Signup: React.FC = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validatePassword = (password: string): boolean => {
    // Password requirements from backend
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*]/.test(password);
    const isLongEnough = password.length >= 8;

    return (
      hasUpperCase &&
      hasLowerCase &&
      hasNumber &&
      hasSpecialChar &&
      isLongEnough
    );
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!validatePassword(form.password)) {
      setError(
        'Password must contain uppercase, lowercase, number, special char, and be 8+ chars'
      );
      return;
    }

    setLoading(true);

    try {
      const response = await authApi.signup({
        name: form.name,
        email: form.email,
        password: form.password,
      });

      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      navigate('/products');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Signup failed'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSignup}>
      <input
        type="text"
        placeholder="Full Name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
        required
      />
      <input
        type="password"
        placeholder="Confirm Password"
        value={form.confirmPassword}
        onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
        required
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Creating account...' : 'Sign Up'}
      </button>
    </form>
  );
};
```

---

## HTTP INTERCEPTOR SETUP

### 5.1 Token Refresh Logic

**CRITICAL: This MUST be implemented exactly as specified.**

When a 401 response is received:

1. Extract the original request
2. Call `POST /api/auth/refresh`
3. Wait for new access token
4. Store new token in localStorage
5. Retry original request with new token
6. If refresh fails, clear storage and redirect to login

```typescript
// Interceptor code (in client.ts - already provided above)
// DO NOT MODIFY the response interceptor logic
```

### 5.2 Request Interceptor

Every request MUST include:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

This is automatically handled by the client interceptor.

### 5.3 Cookie Handling

**CRITICAL: withCredentials MUST be true**

```typescript
withCredentials: true
```

This allows the refresh token cookie to be sent/received automatically.

---

## COMPONENT IMPLEMENTATION GUIDE

### 6.1 Products Component

**API Endpoint**: `GET /api/products/`

**Query Parameters** (ALL optional):
- `niche` (string): Filter by niche
- `platform` (string): Filter by platform
- `region` (string): Filter by region
- `limit` (number): Max results (default: 50, max: 100)
- `offset` (number): Skip N items (default: 0)
- `sort` (string): Sort field and direction, format: "field:direction" (default: "hypeScore:desc")
- `q` (string): Full-text search query

```typescript
// src/api/products.ts
export interface ProductFilters {
  niche?: string;
  platform?: string;
  region?: string;
  limit?: number;
  offset?: number;
  sort?: string;
  q?: string;
}

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

export interface ProductsResponse {
  total: number;
  limit: number;
  offset: number;
  returned: number;
  items: Product[];
}

export const productsApi = {
  listProducts: async (
    filters?: ProductFilters
  ): Promise<ProductsResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get<ProductsResponse>(
      `/api/products/?${params.toString()}`
    );
    return response.data;
  },

  getProduct: async (productId: string): Promise<Product> => {
    const response = await apiClient.get<Product>(
      `/api/products/${productId}`
    );
    return response.data;
  },
};
```

**Products Component Implementation**:

```typescript
// src/pages/Products.tsx
import React, { useState, useEffect } from 'react';
import { productsApi, Product, ProductFilters } from '../api/products';

export const Products: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<ProductFilters>({
    limit: 20,
    offset: 0,
    sort: 'hypeScore:desc',
  });

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  const fetchProducts = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await productsApi.listProducts(filters);
      setProducts(response.items);
      setTotal(response.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: Partial<ProductFilters>) => {
    setFilters({ ...filters, ...newFilters, offset: 0 });
  };

  const handlePagination = (newOffset: number) => {
    setFilters({ ...filters, offset: newOffset });
  };

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="products-container">
      <h1>Products</h1>

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search..."
          onChange={(e) => handleFilterChange({ q: e.target.value })}
        />
        <select
          onChange={(e) => handleFilterChange({ niche: e.target.value })}
          defaultValue=""
        >
          <option value="">All Niches</option>
          <option value="electronics">Electronics</option>
          <option value="clothing">Clothing</option>
          {/* Add more niches */}
        </select>
        <select
          onChange={(e) => handleFilterChange({ platform: e.target.value })}
          defaultValue=""
        >
          <option value="">All Platforms</option>
          <option value="amazon">Amazon</option>
          <option value="shopify">Shopify</option>
          {/* Add more platforms */}
        </select>
      </div>

      {/* Products List */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <>
          <div className="products-grid">
            {products.map((product) => (
              <div key={product.id} className="product-card">
                <h3>{product.title}</h3>
                <p>{product.niche}</p>
                <p>Hype Score: {product.hypeScore}</p>
                <p>Weekly Growth: {product.growthWeekly}%</p>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button
              onClick={() => handlePagination(Math.max(0, filters.offset! - 20))}
              disabled={filters.offset === 0}
            >
              Previous
            </button>
            <span>
              Page {(filters.offset || 0) / 20 + 1} of{' '}
              {Math.ceil(total / 20)}
            </span>
            <button
              onClick={() =>
                handlePagination((filters.offset || 0) + 20)
              }
              disabled={
                (filters.offset || 0) + 20 >= total
              }
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};
```

### 6.2 Saved Searches Component

**API Endpoints**:
- `GET /api/saved-searches/` - List all saved searches
- `POST /api/saved-searches/` - Create new saved search
- `GET /api/saved-searches/{id}` - Get specific search
- `DELETE /api/saved-searches/{id}` - Delete search

```typescript
// src/api/saved-searches.ts
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

export const savedSearchesApi = {
  list: async (): Promise<SavedSearch[]> => {
    const response = await apiClient.get<SavedSearch[]>(
      '/api/saved-searches/'
    );
    return response.data;
  },

  create: async (
    data: CreateSavedSearchRequest
  ): Promise<SavedSearch> => {
    const response = await apiClient.post<SavedSearch>(
      '/api/saved-searches/',
      data
    );
    return response.data;
  },

  get: async (id: string): Promise<SavedSearch> => {
    const response = await apiClient.get<SavedSearch>(
      `/api/saved-searches/${id}`
    );
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/saved-searches/${id}`);
  },
};
```

**Saved Searches Component**:

```typescript
// src/pages/SavedSearches.tsx
import React, { useState, useEffect } from 'react';
import { savedSearchesApi, SavedSearch } from '../api/saved-searches';
import { productsApi } from '../api/products';

export const SavedSearches: React.FC = () => {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [newSearchName, setNewSearchName] = useState('');
  const [newSearchNotes, setNewSearchNotes] = useState('');

  useEffect(() => {
    fetchSearches();
  }, []);

  const fetchSearches = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await savedSearchesApi.list();
      setSearches(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch saved searches');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSearch = async (params: any) => {
    try {
      await savedSearchesApi.create({
        name: newSearchName,
        params,
        notes: newSearchNotes,
      });
      setNewSearchName('');
      setNewSearchNotes('');
      fetchSearches();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create search');
    }
  };

  const handleDeleteSearch = async (id: string) => {
    try {
      await savedSearchesApi.delete(id);
      fetchSearches();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete search');
    }
  };

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="saved-searches-container">
      <h1>Saved Searches</h1>

      {/* Create new search */}
      <div className="create-search">
        <input
          type="text"
          placeholder="Search name"
          value={newSearchName}
          onChange={(e) => setNewSearchName(e.target.value)}
        />
        <textarea
          placeholder="Notes (optional)"
          value={newSearchNotes}
          onChange={(e) => setNewSearchNotes(e.target.value)}
        />
        <button
          onClick={() => handleCreateSearch({ niche: 'electronics' })}
        >
          Save Search
        </button>
      </div>

      {/* List searches */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="searches-list">
          {searches.map((search) => (
            <div key={search.id} className="search-item">
              <h3>{search.name}</h3>
              {search.notes && <p>{search.notes}</p>}
              <p>Created: {new Date(search.createdAt).toLocaleDateString()}</p>
              <button onClick={() => handleDeleteSearch(search.id)}>
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

---

## STATE MANAGEMENT

### 7.1 Zustand Setup (Recommended)

```typescript
// src/store/auth.store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthStore {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  setAccessToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      setUser: (user: User) =>
        set({ user, isAuthenticated: true }),

      setAccessToken: (token: string) =>
        set({ accessToken: token }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

### 7.2 Redux Setup (Alternative)

```typescript
// src/store/auth.slice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
}

const initialState: AuthState = {
  user: null,
  accessToken: null,
  isAuthenticated: false,
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    setAccessToken: (state, action: PayloadAction<string>) => {
      state.accessToken = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.isAuthenticated = false;
    },
  },
});

export const { setUser, setAccessToken, logout } = authSlice.actions;
export default authSlice.reducer;
```

---

## ERROR HANDLING

### 8.1 Error Types

```typescript
// src/types/api.types.ts
export interface ApiError {
  status: number;
  detail: string;
  message?: string;
}

export interface ApiErrorResponse {
  detail: string;
}
```

### 8.2 Error Handler Function

```typescript
// src/utils/errorHandler.ts
import { AxiosError } from 'axios';

export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    // Handle specific status codes
    switch (error.response?.status) {
      case 400:
        return error.response?.data?.detail || 'Bad request';
      case 401:
        return 'Unauthorized - please login again';
      case 403:
        return 'You do not have permission to access this resource';
      case 404:
        return 'Resource not found';
      case 409:
        return error.response?.data?.detail || 'Conflict - resource already exists';
      case 429:
        return 'Too many requests - please wait before trying again';
      case 500:
        return 'Server error - please try again later';
      default:
        return error.response?.data?.detail || 'An error occurred';
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
};
```

### 8.3 Error Boundary Component

```typescript
// src/components/ErrorBoundary.tsx
import React, { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## RESPONSE TYPE DEFINITIONS

### 9.1 TypeScript Types (EXACT definitions)

```typescript
// src/types/api.types.ts

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

## TESTING CHECKLIST

### 10.1 Unit Tests

**MUST test all of the following:**

```typescript
// src/api/__tests__/auth.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authApi } from '../auth';
import * as client from '../client';

vi.mock('../client');

describe('Auth API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ✅ MUST PASS
  it('should signup user successfully', async () => {
    const mockResponse = {
      data: {
        access_token: 'token123',
        refresh_token: 'refresh123',
        user: { id: '1', name: 'John', email: 'john@test.com' },
        token_type: 'bearer',
      },
    };

    vi.spyOn(client.apiClient, 'post').mockResolvedValue(
      mockResponse
    );

    const result = await authApi.signup({
      name: 'John',
      email: 'john@test.com',
      password: 'Password123!',
    });

    expect(result.access_token).toBe('token123');
    expect(result.user.email).toBe('john@test.com');
  });

  // ✅ MUST PASS
  it('should login user successfully', async () => {
    const mockResponse = {
      data: {
        access_token: 'token123',
        user: { id: '1', name: 'John', email: 'john@test.com' },
        token_type: 'bearer',
      },
    };

    vi.spyOn(client.apiClient, 'post').mockResolvedValue(
      mockResponse
    );

    const result = await authApi.login({
      email: 'john@test.com',
      password: 'Password123!',
    });

    expect(result.access_token).toBe('token123');
  });

  // ✅ MUST PASS
  it('should handle login error (401)', async () => {
    const mockError = {
      response: {
        status: 401,
        data: { detail: 'Invalid credentials' },
      },
    };

    vi.spyOn(client.apiClient, 'post').mockRejectedValue(
      mockError
    );

    await expect(
      authApi.login({
        email: 'john@test.com',
        password: 'wrong',
      })
    ).rejects.toThrow();
  });

  // ✅ MUST PASS
  it('should get current user', async () => {
    const mockResponse = {
      data: {
        id: '1',
        name: 'John',
        email: 'john@test.com',
      },
    };

    vi.spyOn(client.apiClient, 'get').mockResolvedValue(
      mockResponse
    );

    const result = await authApi.getCurrentUser();

    expect(result.id).toBe('1');
    expect(result.email).toBe('john@test.com');
  });
});
```

### 10.2 Integration Tests

```typescript
// src/__tests__/integration.test.ts
import { describe, it, expect } from 'vitest';

describe('User Flow Integration', () => {
  // ✅ MUST PASS
  it('should complete full signup and login flow', async () => {
    // 1. Signup
    // 2. Verify token stored
    // 3. Fetch current user
    // 4. Verify user data matches
    expect(true).toBe(true);
  });

  // ✅ MUST PASS
  it('should handle token refresh', async () => {
    // 1. Login
    // 2. Simulate 401 error
    // 3. Verify refresh token called
    // 4. Verify request retried
    expect(true).toBe(true);
  });

  // ✅ MUST PASS
  it('should redirect to login on refresh failure', async () => {
    // 1. Simulate refresh failure
    // 2. Verify localStorage cleared
    // 3. Verify redirect to /login
    expect(true).toBe(true);
  });
});
```

### 10.3 Manual Testing Scenarios

**CRITICAL: All must pass before deployment**

- [ ] User can sign up with valid email and password
- [ ] User cannot sign up with duplicate email (409 error)
- [ ] User receives error for weak password
- [ ] User can login with correct credentials
- [ ] User gets 401 for incorrect password
- [ ] User can logout successfully
- [ ] User can request password reset
- [ ] User can reset password with valid token
- [ ] User can browse products without filters
- [ ] User can filter products by niche
- [ ] User can search products by text
- [ ] User can paginate through products
- [ ] User can create saved search
- [ ] User can list saved searches
- [ ] User can delete saved search
- [ ] Token automatically refreshes on 401
- [ ] User is redirected to login on refresh failure
- [ ] API rate limiting returns 429 error
- [ ] CORS headers present in responses
- [ ] Security headers present in responses

---

## DEPLOYMENT CHECKLIST

### 11.1 Pre-Deployment Checks

**BEFORE deploying to production:**

```bash
# ✅ Run tests
npm run test

# ✅ Type check
npm run type-check

# ✅ Build
npm run build

# ✅ No console errors
npm run build:prod

# ✅ Verify .env.production is correct
cat .env.production
```

### 11.2 Environment Variables Verification

**Production .env.production MUST have:**

```
✅ VITE_API_BASE_URL=https://production-api.com
✅ VITE_GOOGLE_CLIENT_ID=production-id
✅ VITE_ENABLE_DEBUG_MODE=false
✅ VITE_ENABLE_EMAIL_VERIFICATION=true
```

**Development .env.local MUST have:**

```
✅ VITE_API_BASE_URL=http://localhost:8000
✅ VITE_API_TIMEOUT=10000
✅ VITE_ENABLE_DEBUG_MODE=true
```

### 11.3 API Connectivity Tests

**MUST verify before deploying:**

```bash
# ✅ Backend is running
curl http://localhost:8000/healthz
# Response: {"status": "ok"}

# ✅ CORS is working
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     http://localhost:8000/api/auth/login

# ✅ Auth endpoint works
curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"test"}'
```

### 11.4 Browser DevTools Checks

**Open DevTools (F12) and verify:**

- [ ] No console errors
- [ ] Authorization header present in API requests
- [ ] Bearer token format correct: `Bearer eyJhbGc...`
- [ ] Refresh token cookie present (httpOnly)
- [ ] CORS headers present in responses
- [ ] Network requests showing correct status codes
- [ ] LocalStorage has `access_token` after login
- [ ] No sensitive data in LocalStorage (except token)

### 11.5 Deployment Steps

```bash
# 1. Build production bundle
npm run build

# 2. Verify build output
ls -la dist/

# 3. Deploy to hosting (example: Vercel)
npm run deploy

# 4. Test deployed application
# - Open https://your-app.com
# - Login with test account
# - Browse products
# - Create saved search
# - Verify all features work

# 5. Monitor errors
# - Check browser console
# - Check backend logs
# - Monitor API responses
```

### 11.6 Post-Deployment Checklist

**After deployment:**

- [ ] Frontend loads without errors
- [ ] Login page works
- [ ] Can signup new user
- [ ] Can login existing user
- [ ] Products load
- [ ] Can filter products
- [ ] Can create saved searches
- [ ] Token refresh works (wait >2min, make API call)
- [ ] Logout clears data
- [ ] Backend health check passes
- [ ] All API endpoints respond correctly
- [ ] No CORS errors in console
- [ ] Response times acceptable (<2s)
- [ ] Rate limiting triggers correctly
- [ ] Error messages display properly

### 11.7 Monitoring & Logs

**Track these metrics:**

```
✅ Error rate < 0.1%
✅ API response time < 1s (median)
✅ Token refresh success rate > 99%
✅ 401 errors decrease after refresh
✅ No infinite redirect loops
✅ CORS errors = 0
✅ All 200/201/204 responses expected
```

---

## CRITICAL RULES - DO NOT DEVIATE

### 12.1 Token Management

```
✅ REQUIRED: withCredentials: true in axios
✅ REQUIRED: Authorization: Bearer <token> header
✅ REQUIRED: Refresh token in httpOnly cookie
✅ REQUIRED: Auto-retry on 401 with new token
✅ PROHIBITED: Storing sensitive data in LocalStorage
✅ PROHIBITED: Exposing token in URLs
```

### 12.2 Error Handling

```
✅ REQUIRED: Handle 401 with token refresh
✅ REQUIRED: Handle 429 with rate limit message
✅ REQUIRED: Handle 409 with duplicate message
✅ REQUIRED: Log all errors for debugging
✅ PROHIBITED: Showing raw API errors to users
✅ PROHIBITED: Redirecting without clearing tokens
```

### 12.3 API Calls

```
✅ REQUIRED: Query params correctly formatted
✅ REQUIRED: Request body in JSON format
✅ REQUIRED: Authorization header on protected routes
✅ REQUIRED: Content-Type: application/json
✅ PROHIBITED: Direct fetch() calls (use apiClient)
✅ PROHIBITED: Multiple token refresh attempts
```

### 12.4 Component Implementation

```
✅ REQUIRED: Validate user input before sending
✅ REQUIRED: Show loading state during API calls
✅ REQUIRED: Display error messages from API
✅ REQUIRED: Handle empty/null responses
✅ REQUIRED: Type all props with TypeScript
✅ PROHIBITED: Making API calls on every render
✅ PROHIBITED: Storing API responses in state multiple times
✅ PROHIBITED: Missing error boundaries
```

### 12.5 Security

```
✅ REQUIRED: Use https in production
✅ REQUIRED: Validate all user input
✅ REQUIRED: Clear tokens on logout
✅ REQUIRED: Use environment variables for secrets
✅ REQUIRED: Redirect unauthorized access to login
✅ PROHIBITED: Storing passwords anywhere
✅ PROHIBITED: Logging sensitive data
✅ PROHIBITED: Using eval() or innerHTML with user data
```

---

## QUICK START TEMPLATE

### 13.1 Minimal Working Frontend

```typescript
// App.tsx
import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Products } from './pages/Products';
import { SavedSearches } from './pages/SavedSearches';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />
        <Route
          path="/signup"
          element={<Signup />}
        />
        <Route
          path="/products"
          element={
            isAuthenticated ? <Products /> : <Navigate to="/login" />
          }
        />
        <Route
          path="/saved-searches"
          element={
            isAuthenticated ? <SavedSearches /> : <Navigate to="/login" />
          }
        />
        <Route path="/" element={<Navigate to="/products" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### 13.2 Main.tsx

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { GoogleOAuthProvider } from '@react-oauth/google'
import App from './App.tsx'
import './index.css'

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={googleClientId}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>,
)
```

---

## SUPPORT & TROUBLESHOOTING

### 14.1 Common Issues

**Issue**: 401 Unauthorized on every request

```
✅ Check: localStorage has access_token
✅ Check: Token format is "Bearer <token>"
✅ Check: Token hasn't expired
✅ Solution: Re-login or refresh token
```

**Issue**: CORS errors in console

```
✅ Check: Backend CORS allows frontend origin
✅ Check: withCredentials: true in axios
✅ Check: API_BASE_URL correct in .env
✅ Solution: Verify backend CORS config
```

**Issue**: Token not refreshing

```
✅ Check: refresh_token cookie sent with requests
✅ Check: withCredentials: true in axios
✅ Check: Refresh endpoint returns new token
✅ Solution: Clear cache and re-login
```

**Issue**: Infinite redirect loop

```
✅ Check: Login page accessible without token
✅ Check: Token refresh success rate > 90%
✅ Check: No redirect on logout page
✅ Solution: Add redirect guard in routes
```

### 14.2 Debug Mode

Enable debug logging:

```typescript
// .env.local
VITE_ENABLE_DEBUG_MODE=true

// In apiClient.ts
if (import.meta.env.VITE_ENABLE_DEBUG_MODE) {
  console.log('Request:', config);
  console.log('Response:', response.data);
}
```

### 14.3 Network Tab Analysis

**Check DevTools Network tab:**

1. Click any API request
2. Verify headers:
   - `Authorization: Bearer <token>`
   - `Content-Type: application/json`
   - `Origin: http://localhost:3000`
3. Verify response headers:
   - `Access-Control-Allow-Origin: http://localhost:3000`
   - `Access-Control-Allow-Credentials: true`
4. Verify response body matches TypeScript types

---

## FINAL CHECKLIST

Before marking Frontend Integration Complete:

- [ ] All environment variables configured
- [ ] HTTP client with interceptors created
- [ ] All 8 auth endpoints implemented
- [ ] Login/Signup components working
- [ ] Token refresh automatic on 401
- [ ] Products component with filters
- [ ] Saved searches CRUD working
- [ ] Error handling for all scenarios
- [ ] State management setup (Zustand or Redux)
- [ ] TypeScript types for all API responses
- [ ] Token cleared on logout
- [ ] Protected routes working
- [ ] All tests passing
- [ ] No console errors
- [ ] API connectivity verified
- [ ] CORS working
- [ ] Rate limiting handled
- [ ] Security headers verified
- [ ] Deployment ready

---

**Document Version**: 1.0  
**Status**: Ready for Frontend Development  
**Last Updated**: November 13, 2025
