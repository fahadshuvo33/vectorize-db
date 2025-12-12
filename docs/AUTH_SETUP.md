# Authentication System Setup

This document explains the complete authentication system for VectorizeDB.

## Features

✅ **Email/Password Authentication**
- User registration with email and password
- Email verification requirement to access dashboard
- Password reset via email
- Secure password hashing with bcrypt

✅ **Social Authentication (OAuth)**
- Google OAuth login
- GitHub OAuth login
- Auto-creates profile on first social login
- Social accounts can add password later

✅ **Email Verification**
- Automatic verification email sent on registration
- Verification required before accessing dashboard
- Resend verification email option
- Supabase handles email delivery

✅ **Password Management**
- Social login users can add password later
- Change password for existing accounts
- Password reset flow
- Secure password requirements (min 8 characters)

✅ **Profile Management**
- Get user profile
- Update profile (name, avatar)
- View connected social accounts
- Referral code system

## API Endpoints

### Registration & Login

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "full_name": "John Doe",
  "referral_code": "ABC12345" // optional
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}
```

### Social Authentication

#### Get OAuth URL
```http
GET /api/v1/auth/oauth/google
GET /api/v1/auth/oauth/github
```

Response:
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### Password Management

#### Set Password (for social accounts)
```http
POST /api/v1/auth/set-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

#### Reset Password
```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Email Verification

#### Verify Email
```http
POST /api/v1/auth/verify-email
Content-Type: application/json

{
  "token": "verification_token_from_email"
}
```

#### Resend Verification
```http
POST /api/v1/auth/resend-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### User Profile

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

#### Get Full Profile
```http
GET /api/v1/auth/profile
Authorization: Bearer <token>
```

Response includes:
- User details
- Connected social accounts
- Whether user has password set
- Referral information

#### Update Profile
```http
PATCH /api/v1/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

## Setup Instructions

### 1. Supabase Configuration

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Go to **Authentication** > **Providers**
3. Enable **Email** provider
4. Enable **Google** OAuth (add Client ID and Secret)
5. Enable **GitHub** OAuth (add Client ID and Secret)

### 2. Environment Variables

Update your `.env` file with:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # Optional

# Frontend
FRONTEND_URL=http://localhost:5173

# OAuth (from Supabase provider settings)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Email (optional - Supabase handles this)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@vectorizedb.com
SMTP_FROM_NAME=VectorizeDB

# Security
SECRET_KEY=your-super-secret-key-change-in-production
REQUIRE_EMAIL_VERIFICATION=true
```

### 3. Database Tables

The authentication system uses these Supabase tables:

- **profiles** - User profile data (auto-created on registration)
- **social_logins** - OAuth connection records
- **auth.users** - Supabase auth table (managed by Supabase)

Run the SQL migration to create tables:

```sql
-- profiles table
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  avatar_url TEXT,
  current_plan TEXT DEFAULT 'basic',
  plan_ends_at TIMESTAMPTZ,
  referral_code TEXT UNIQUE,
  referred_by UUID REFERENCES profiles(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- social_logins table
CREATE TABLE social_logins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  email TEXT NOT NULL,
  name TEXT,
  avatar_url TEXT,
  raw_data JSONB,
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(provider, provider_id)
);

-- Indexes
CREATE INDEX idx_profiles_referral_code ON profiles(referral_code);
CREATE INDEX idx_social_logins_user_id ON social_logins(user_id);
CREATE INDEX idx_social_logins_provider ON social_logins(provider, provider_id);
```

### 4. Email Templates (Supabase)

Configure email templates in Supabase:

1. Go to **Authentication** > **Email Templates**
2. Customize templates for:
   - Confirmation email
   - Magic link
   - Password reset
   - Email change

## Authentication Flow

### Email Registration Flow
1. User submits registration form
2. Backend creates user in Supabase Auth
3. Backend creates profile in `profiles` table
4. Supabase sends verification email automatically
5. User clicks link in email to verify
6. User can now access dashboard

### Social Login Flow
1. User clicks "Login with Google/GitHub"
2. Frontend calls `/api/v1/auth/oauth/{provider}`
3. User is redirected to OAuth provider
4. OAuth provider redirects back with tokens
5. Backend exchanges tokens with Supabase
6. Profile is created if first login
7. User is logged in

### Add Password to Social Account Flow
1. User logged in with social account
2. User calls `/api/v1/auth/set-password` with new password
3. Backend updates Supabase Auth user with password
4. User can now login with email/password OR social

## Protected Routes

Use dependencies to protect routes:

```python
from app.core.dependencies import get_current_user, get_verified_user

# Requires authentication only
@router.get("/dashboard")
async def dashboard(user: dict = Depends(get_current_user)):
    return {"message": "Welcome to dashboard"}

# Requires verified email
@router.post("/upload")
async def upload(user: dict = Depends(get_verified_user)):
    return {"message": "File uploaded"}
```

## Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token validation
- ✅ Email verification requirement
- ✅ OAuth state validation (Supabase)
- ✅ Rate limiting (TODO)
- ✅ CORS configuration
- ✅ Secure token storage

## Testing

Test the authentication with:

```bash
# Start the server
docker-compose up

# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345","full_name":"Test User"}'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test12345"}'

# Test protected endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Frontend Integration

### Login Example
```javascript
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Store token
  localStorage.setItem('access_token', data.access_token);
  
  return data.user;
};
```

### Social Login Example
```javascript
const loginWithGoogle = async () => {
  // Get OAuth URL
  const response = await fetch('http://localhost:8000/api/v1/auth/oauth/google');
  const { url } = await response.json();
  
  // Redirect to OAuth
  window.location.href = url;
};

// On callback page
const handleOAuthCallback = () => {
  // Extract tokens from URL (Supabase handles this)
  const params = new URLSearchParams(window.location.hash.substring(1));
  const access_token = params.get('access_token');
  
  if (access_token) {
    localStorage.setItem('access_token', access_token);
    // Redirect to dashboard
  }
};
```

### Protected API Calls
```javascript
const fetchProtected = async (url) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 403) {
    // Email not verified
    alert('Please verify your email to access this feature');
  }
  
  return response.json();
};
```

## Troubleshooting

### Email verification not working
- Check Supabase email settings
- Verify SMTP configuration
- Check spam folder
- Confirm email provider settings in Supabase

### OAuth not working
- Verify OAuth credentials in Supabase
- Check redirect URLs match
- Ensure provider is enabled in Supabase
- Check OAuth consent screen settings

### Token validation failing
- Verify SUPABASE_URL and SUPABASE_KEY are correct
- Check token expiration
- Ensure token is sent in Authorization header

## Next Steps

1. ✅ Complete email verification flow
2. ✅ Add social login providers
3. ✅ Implement password management
4. ⏳ Add rate limiting
5. ⏳ Add session management
6. ⏳ Add 2FA (optional)
7. ⏳ Add OAuth token refresh
