# 🔐 Social Authentication & Email Service Setup Guide

Complete setup guide for implementing Google and GitHub OAuth authentication plus email services in ApplyAI.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Configuration](#environment-configuration)
3. [Email Service Setup](#email-service-setup)
4. [OAuth Provider Setup](#oauth-provider-setup)
5. [Frontend Configuration](#frontend-configuration)
6. [Testing & Verification](#testing--verification)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)
9. [Production Deployment](#production-deployment)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Gmail account (for email service)
- Developer accounts with OAuth providers

### Installation
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

---

## ⚙️ Environment Configuration

### 1. Create Backend Environment File

Create `backend/.env` with the following configuration:

```env
# ===== CORE CONFIGURATION =====
OPENAI_API_KEY=sk-your-openai-api-key-here
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-minimum-32-characters

# ===== DATABASE =====
DATABASE_URL=sqlite:///./applyai.db
# For production, choose ONE of the following:
# PostgreSQL (recommended): postgresql://username:password@localhost/applyai
# MySQL (alternative): mysql://username:password@localhost/applyai

# ===== EMAIL SERVICE =====
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_USE_TLS=true
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=ApplyAI

# ===== OAUTH PROVIDERS =====
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# ===== SECURITY & PERFORMANCE =====
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
TRUSTED_HOSTS=localhost,127.0.0.1
ENVIRONMENT=development
DEBUG=true
RATE_LIMIT_PER_MINUTE=60
MAX_FILE_SIZE=10485760
```

### 2. Create Frontend Environment File

Create `frontend/.env.local`:

```env
# Development
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production
# NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## 📧 Email Service Setup

### Option 1: Gmail (Recommended)

#### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification"

#### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" as the app
3. Copy the generated 16-character password
4. Use this as your `SMTP_PASSWORD` in `.env`

#### Step 3: Configure Environment
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_USE_TLS=true
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=ApplyAI
```

### Option 2: Other Email Providers

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

#### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

#### Custom SMTP
```env
SMTP_SERVER=mail.your-domain.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

---

## 🔑 OAuth Provider Setup

### Google OAuth Setup

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Google+ API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

#### Step 2: Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Configure consent screen if prompted
4. Application type: "Web application"
5. Add authorized redirect URIs:
   ```
   http://localhost:3000/auth/callback/google
   https://yourdomain.com/auth/callback/google
   ```

#### Step 3: Configure Environment
```env
GOOGLE_CLIENT_ID=1234567890-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret-here
```

### GitHub OAuth Setup

#### Step 1: Create GitHub OAuth App
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in details:
   - **Application name**: ApplyAI
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/auth/callback/github`

#### Step 2: Configure Environment
```env
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

---

## 💻 Frontend Configuration

### Update Next.js Configuration

Ensure your `frontend/next.config.js` includes:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

---

## 🧪 Testing & Verification

### 1. Start the Services

#### Terminal 1: Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

#### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### 2. Test Email Service

#### Register a New User
1. Go to `http://localhost:3000/register`
2. Create account with your email
3. Check your email for verification message
4. Verify the email contains proper links and styling

#### Test Password Reset
1. Go to `http://localhost:3000/forgot-password`
2. Enter your email address
3. Check email for reset link
4. Complete password reset process

### 3. Test Social Authentication

#### Google Authentication
1. Go to `http://localhost:3000/login`
2. Click "Continue with Google"
3. Complete OAuth flow
4. Verify user is created in database
5. Test logout and re-login

#### GitHub Authentication
1. Click "Continue with GitHub"
2. Complete OAuth flow
3. Verify profile data is imported
4. Test logout and re-login

### 4. Test API Endpoints

#### Test Auth Endpoints
```bash
# Get OAuth URLs
curl http://localhost:8000/auth/oauth/urls

# Test protected endpoint
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/auth/me
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Google OAuth Issues
- **Issue**: "redirect_uri_mismatch" error
- **Solution**: Ensure OAuth redirect URIs match exactly in Google Cloud Console

#### 2. Email Service Issues
- **Issue**: SMTP authentication failed
- **Solution**: Use Gmail App Password, not regular password

#### 3. GitHub OAuth Issues
- **Issue**: "incorrect_client_credentials" error
- **Solution**: Verify GitHub OAuth app settings and client credentials

#### 4. CORS Issues
- **Issue**: Cross-origin requests blocked
- **Solution**: Update `ALLOWED_ORIGINS` in backend `.env`

#### 5. Database Connection Issues
- **Issue**: Database connection failed
- **Solution**: Ensure database URL is correct and database is running

### Debug Mode

Enable debug logging in `backend/.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

Check logs for detailed error messages:
```bash
cd backend
python -m uvicorn main:app --reload --log-level debug
```

---

## 🛡️ Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to version control
- Use different secrets for development/production
- Rotate secrets regularly

### 2. OAuth Security
- Use HTTPS in production
- Validate all OAuth tokens on the server
- Implement proper session management

### 3. Email Security
- Use dedicated email service for production
- Implement rate limiting for email endpoints
- Validate email addresses before sending

### 4. API Security
- Implement proper CORS configuration
- Use rate limiting on auth endpoints
- Validate all inputs and sanitize data

---

## 🚀 Production Deployment

### 1. Environment Setup

#### Production Environment Variables
```env
# Production backend .env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=your-production-jwt-secret-64-chars-minimum
DATABASE_URL=postgresql://username:password@localhost/applyai_prod

# Email Service
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAIL_FROM=no-reply@yourdomain.com

# OAuth Providers
GOOGLE_CLIENT_ID=your-prod-google-client-id
GOOGLE_CLIENT_SECRET=your-prod-google-client-secret
GITHUB_CLIENT_ID=your-prod-github-client-id
GITHUB_CLIENT_SECRET=your-prod-github-client-secret

# Security
ALLOWED_ORIGINS=https://yourdomain.com
TRUSTED_HOSTS=yourdomain.com
RATE_LIMIT_PER_MINUTE=30
```

### 2. OAuth Provider Configuration

#### Update OAuth Redirect URIs
1. **Google**: Update app URLs to production domain
2. **GitHub**: Update app URLs to production domain

Add production URLs:
```
https://yourdomain.com/auth/callback/google
https://yourdomain.com/auth/callback/github
```

### 3. Deployment Checklist

#### Pre-Deployment
- [ ] Production database configured
- [ ] Email service configured (SendGrid, etc.)
- [ ] OAuth apps updated with production URLs
- [ ] SSL certificates installed
- [ ] Environment variables configured

#### Post-Deployment
- [ ] Email verification works
- [ ] Google OAuth login works
- [ ] GitHub OAuth login works
- [ ] Database migrations applied
- [ ] HTTPS enforced

---

## 📚 Additional Resources

### Documentation
- [FastAPI OAuth2 Documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)

### Tools
- [JWT.io](https://jwt.io/) - JWT token decoder
- [Postman](https://www.postman.com/) - API testing
- [OAuth2 Debugger](https://oauthdebugger.com/) - OAuth flow testing

---

## ✅ Setup Checklist

### Development Setup
- [ ] Python virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Gmail account configured with 2FA
- [ ] Gmail App Password generated
- [ ] Backend `.env` file created
- [ ] Frontend `.env.local` file created

### OAuth Provider Setup
- [ ] Google Cloud project created
- [ ] Google OAuth2 credentials configured
- [ ] GitHub OAuth app created and configured
- [ ] OAuth redirect URIs configured correctly

### Testing
- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Email verification works
- [ ] Google OAuth login works
- [ ] GitHub OAuth login works
- [ ] Database operations work correctly

### Production Readiness
- [ ] Production database configured
- [ ] Production email service configured
- [ ] OAuth providers updated for production
- [ ] SSL certificates configured
- [ ] Environment variables secured
- [ ] Monitoring and logging configured

---

**Need help?** Check the troubleshooting section or create an issue in the repository! 