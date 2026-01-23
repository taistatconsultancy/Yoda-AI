# 🚀 YodaAI Vercel Deployment Guide

Complete guide to deploying YodaAI on Vercel with all dependencies and configurations.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Vercel Deployment Architecture](#vercel-deployment-architecture)
3. [Prerequisites](#prerequisites)
4. [Critical Considerations](#critical-considerations)
5. [Deployment Methods](#deployment-methods)
6. [Environment Variables](#environment-variables)
7. [Database Configuration](#database-configuration)
8. [File Structure Setup](#file-structure-setup)
9. [Step-by-Step Deployment](#step-by-step-deployment)
10. [Troubleshooting](#troubleshooting)
11. [Alternative Deployment Options](#alternative-deployment-options)

---

## 📖 Overview

YodaAI is a FastAPI-based application with the following characteristics:

- **Backend**: FastAPI with Python 3.9+ runtime
- **Database**: Neon PostgreSQL (cloud-hosted)
- **Static Assets**: HTML frontend files in `app/ui/`
- **Dependencies**: 150+ Python packages including heavy ML/AI libraries
- **External Services**: OpenAI API, Firebase (optional), SMTP (optional)

### Application Architecture

```
YodaAI Application
├── FastAPI Backend (main.py)
│   ├── API Routes (authentication, workspaces, retrospectives, etc.)
│   ├── AI Services (GPT-4, grouping, recommendations)
│   ├── Database (Neon PostgreSQL via SQLAlchemy)
│   └── Static File Serving (HTML, CSS, JS)
└── Frontend (app/ui/)
    ├── yodaai-app.html (main dashboard)
    └── retrospective.html (retrospective session UI)
```

---

## 🏗️ Vercel Deployment Architecture

### **Challenge**: FastAPI + Heavy Dependencies

Your application has several deployment considerations:

| Component | Challenge | Solution |
|-----------|-----------|----------|
| **Python Runtime** | Vercel supports Python but with limitations | ✅ Use serverless functions |
| **Large Dependencies** | 150+ packages, ML libraries may exceed size limits | ⚠️ Optimize requirements.txt |
| **Database Connections** | Connection pooling in serverless | ✅ Use Neon with connection pooling |
| **Static Files** | Large HTML files need to be served | ✅ Use `StaticFiles` or CDN |
| **File Uploads** | PDF uploads need storage | ✅ Use external storage (S3, etc.) |
| **Long-Running Processes** | AI processing, PDF generation | ⚠️ Vercel has timeout limits |
| **State Management** | Polling, websockets | ⚠️ May not work in serverless |

### **Recommended Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                     Vercel Platform                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Serverless Functions (Python 3.12)        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │
│  │  │   API    │  │   API    │  │   API    │  ...  │  │
│  │  │ Routes   │  │ Routes   │  │ Routes   │       │  │
│  │  └──────────┘  └──────────┘  └──────────┘       │  │
│  │         │              │              │          │  │
│  └─────────┼──────────────┼──────────────┼──────────┘  │
│            │              │              │             │
│  ┌─────────┴──────────────┴──────────────┴──────────┐ │
│  │           Static Files (HTML/CSS/JS)              │ │
│  │  - yodaai-app.html                                │ │
│  │  - retrospective.html                             │ │
│  └───────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
            │                      │                      │
            │                      │                      │
    ┌───────▼────────┐    ┌────────▼────────┐    ┌──────▼──────┐
    │ Neon PostgreSQL│    │  OpenAI API     │    │   Other     │
    │   (Database)   │    │  (AI Services)  │    │  Services   │
    └────────────────┘    └─────────────────┘    └─────────────┘
```

---

## ✅ Prerequisites

### **Required Accounts**

1. **Vercel Account** 
   - Sign up at: https://vercel.com
   - Free tier includes: 100GB bandwidth, 100 hours build time
   
2. **Neon Account**
   - Sign up at: https://neon.tech
   - Free tier includes: 0.5GB storage, shared compute
   
3. **OpenAI Account**
   - Sign up at: https://platform.openai.com
   - Get API key: https://platform.openai.com/api-keys
   - **Important**: Enable billing for production use

### **Development Tools**

- **Git** (latest version)
- **Node.js** (v18+ for Vercel CLI)
- **Python** (3.9+ for local testing)
- **Vercel CLI**: `npm install -g vercel`

---

## ⚠️ Critical Considerations

### **1. Serverless Function Limits**

| Limit | Free Tier | Pro Tier | Impact on YodaAI |
|-------|-----------|----------|------------------|
| **Max Function Duration** | 10 seconds | 60 seconds | ⚠️ Some AI calls may timeout |
| **Max Request Size** | 4.5 MB | 4.5 MB | ⚠️ PDF uploads may fail |
| **Max Response Size** | 4.5 MB | 4.5 MB | ⚠️ Large AI responses may fail |
| **Max Build Time** | 45 minutes | 60 minutes | ✅ Should be sufficient |
| **Function Size Limit** | 50 MB (uncompressed) | 250 MB | ⚠️ Heavy ML libraries |

### **2. Cold Start Issues**

Serverless functions have **cold starts** - first request after inactivity is slower:
- **Python**: 500ms - 2s cold start
- **Impact**: Users may experience latency on first API call
- **Mitigation**: Keep-alive pings or use Vercel Pro (faster startups)

### **3. Database Connection Pooling**

**Challenge**: Each serverless function creates its own database connection.

**Solution**: 
- Neon supports connection pooling with pgbouncer
- Configure SQLAlchemy for serverless:
  ```python
  # Use NullPool in serverless environment
  engine_kwargs["poolclass"] = NullPool
  ```

### **4. Static File Serving**

Large HTML files (yodaai-app.html is 5764 lines):
- ✅ Vercel can serve static files efficiently
- ✅ Use CDN caching
- ⚠️ Ensure paths are correct in production

### **5. Environment Variables**

**Security**: Never commit sensitive keys to Git!

- Use Vercel's environment variable settings
- Different variables for Production/Preview/Development
- Consider using Vercel Secrets for additional security

---

## 🎯 Deployment Methods

### **Method 1: Full Application Deploy (Recommended)**

Deploy entire FastAPI app as serverless functions with static files.

**Pros:**
- Single deployment
- All features available
- Easy to maintain

**Cons:**
- May hit function size limits
- Cold starts
- Some features may need adjustments

### **Method 2: Hybrid Deployment**

- API on Vercel (serverless)
- Frontend on separate CDN (Cloudflare Pages, Netlify)
- Database on Neon

**Pros:**
- Optimized for each layer
- Better performance
- More flexibility

**Cons:**
- More complex setup
- CORS configuration needed
- Multiple deployments

### **Method 3: Container Deployment (Alternative)**

Use Railway, Render, or Fly.io for full VM deployment.

**Pros:**
- No size limits
- Full control
- Stateful connections

**Cons:**
- Not using Vercel
- Higher cost
- Different deployment process

**For this guide, we'll use Method 1 (Full Vercel Deployment)**

---

## 📝 Required Environment Variables

### **Critical Variables (Required)**

```bash
# Database
NEON_DATABASE_URL=postgresql://username:password@host/database?sslmode=require
USE_LOCAL_DB=False

# OpenAI (REQUIRED for AI features)
OPENAI_API_KEY=sk-your-openai-api-key-here

# JWT Authentication
SECRET_KEY=your-super-secret-key-min-32-characters-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### **Optional but Recommended**

```bash
# Application
DEBUG=False
ENVIRONMENT=production
APP_URL=https://your-app.vercel.app

# Feature Flags
ENABLE_EMAIL_NOTIFICATIONS=True
ENABLE_AI_ANALYSIS=True

# Email Service (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@yodaai.com
```

### **Optional AI Services**

```bash
# Gemini (alternative to OpenAI)
GEMINI_API_KEY=your-gemini-key

# Hugging Face
HUGGINGFACE_API_KEY=your-hf-key
HF_TOKEN=your-hf-token

# Chroma
CHROMA_API_KEY=your-chroma-key
```

### **Firebase (Optional - for Google OAuth)**

```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@project.iam.gserviceaccount.com
```

---

## 🗄️ Database Configuration

### **Neon PostgreSQL Setup**

1. **Create Neon Project**
   - Go to: https://console.neon.tech/
   - Click "Create Project"
   - Choose region closest to your users
   - Note the connection string

2. **Run Database Migrations**

   Option A: From Neon SQL Editor
   ```sql
   -- Copy all SQL from app/docs/database/database_schema_complete.sql
   -- Paste and run in Neon SQL Editor
   ```

   Option B: Using Alembic (if supported on Vercel)
   ```bash
   # This may not work on Vercel due to build constraints
   alembic upgrade head
   ```

   **Recommendation**: Use Option A (SQL Editor) for reliability.

3. **Enable Connection Pooling**

   Neon provides pooled connections:
   - Regular connection: `postgresql://...`
   - Pooled connection: `postgresql://...?pgbouncer=true`
   
   **Use pooled connection** for better serverless performance!

   ```bash
   NEON_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require&pgbouncer=true
   ```

---

## 📁 File Structure Setup

### **Required Files for Vercel**

Create these files in your project root:

```
V3_Assistant/
├── main.py                    # ✅ Already exists - FastAPI entry point
├── requirements.txt           # ✅ Already exists - Dependencies
├── vercel.json                # ❌ NEED TO CREATE - Vercel config
├── .vercelignore              # ❌ NEED TO CREATE - Ignore patterns
├── runtime.txt                # ❌ NEED TO CREATE - Python version
└── app/                       # ✅ Already exists
    ├── ui/                    # ✅ Static files
    └── ...
```

---

## 📋 Step-by-Step Deployment

### **Step 1: Prepare Project Files**

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    },
    {
      "src": "app/ui/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/main.py"
    },
    {
      "src": "/ui/(.*)",
      "dest": "/app/ui/$1"
    },
    {
      "src": "/",
      "dest": "/app/ui/yodaai-app.html"
    },
    {
      "src": "/(.*)",
      "dest": "/main.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

Create `runtime.txt`:

```txt
python-3.11.0
```

Create `.vercelignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
ai/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Local files
*.db
*.log
.env
.env.local
*.sqlite

# Build artifacts
build/
dist/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Documentation
app/docs/
*.md
!README.md

# Alembic (not needed in production)
alembic/
alembic.ini

# Utility scripts
check_*.py
fix_*.py
quick_*.py
sync_*.py
start_server.py
test_*.py
get_verification_link.py

# Backup files
*.bak

# Project docs
*_STATUS.md
*_COMPLETE.md
*_READY.md
*_IMPLEMENTATION.md
*_UPDATE*.md
*_FIX*.md
BATCH_*.md
COMPLETE_*.md
EMAIL_*.md
FINAL_*.md
FIREBASE_*.md
GOOGLE_*.md
IMPLEMENTATION_*.md
INVITATION_*.md
SESSION_*.md
UI_*.md
VOTING_*.md

# Deployment docs
DEPLOYMENT_*.md
VERCEL_*.md

# Other
.pytest_cache/
.mypy_cache/
.dmypy.json
dmypy.json
```

### **Step 2: Optimize Requirements**

Create `requirements-prod.txt` (minimal production dependencies):

```txt
fastapi==0.118.2
uvicorn==0.37.0
pydantic==2.12.0
pydantic-settings==2.11.0
python-dotenv==1.1.1
python-jose==3.5.0
bcrypt==5.0.0
sqlalchemy==2.0.43
psycopg2==2.9.11
openai==2.3.0
reportlab==4.0.9
email-validator==2.3.0
python-multipart==0.0.20
cryptography==46.0.2
requests==2.32.5
python-dateutil==2.9.0.post0

# Optional - only if using
# firebase-admin==7.1.0
# chromadb==1.1.1
# langchain==0.3.27
```

**Note**: Heavy packages like `chromadb`, `langchain`, `firebase_admin` can cause size issues.
Add them only if absolutely necessary.

### **Step 3: Initialize Git Repository**

```bash
# Navigate to project directory
cd C:\Users\savin\Desktop\Taistat\AI_assistant\V3_Assistant

# Initialize git if not already done
git init

# Create .gitignore if not exists
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
echo "ai/" >> .gitignore

# Add and commit files
git add .
git commit -m "Prepare for Vercel deployment"
```

### **Step 4: Create Vercel Project**

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (will prompt for configuration)
vercel

# When prompted:
# - "Set up and deploy?": Yes
# - "Project name": yoda-ai
# - "Directory": ./
# - "Override settings?": No (first time)
```

**Option B: Using GitHub Integration**

1. Push code to GitHub:
   ```bash
   # Create GitHub repo and push
   git remote add origin https://github.com/yourusername/yoda-ai.git
   git branch -M main
   git push -u origin main
   ```

2. Import in Vercel:
   - Go to: https://vercel.com/dashboard
   - Click "Add New Project"
   - Import from GitHub
   - Select your repository

### **Step 5: Configure Environment Variables**

In Vercel Dashboard:

1. Go to **Project Settings** → **Environment Variables**
2. Add each variable:

```
NEON_DATABASE_URL: postgresql://...?sslmode=require&pgbouncer=true
OPENAI_API_KEY: sk-...
SECRET_KEY: [generate with: openssl rand -hex 32]
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 480
USE_LOCAL_DB: False
DEBUG: False
ENVIRONMENT: production
APP_URL: https://your-app.vercel.app
```

3. **Important**: Set scope to "Production", "Preview", and "Development"

4. If using email, add SMTP variables:
   ```
   SMTP_HOST: smtp.gmail.com
   SMTP_PORT: 587
   SMTP_USER: your-email@gmail.com
   SMTP_PASSWORD: your-app-password
   SMTP_FROM_EMAIL: noreply@yodaai.com
   SMTP_FROM_NAME: YodaAI
   ```

### **Step 6: Redeploy**

```bash
# After adding environment variables, redeploy
vercel --prod
```

### **Step 7: Test Deployment**

1. **Check Health Endpoint**
   ```
   https://your-app.vercel.app/health
   ```
   Expected: `{"status": "healthy", "service": "yodaai"}`

2. **Test API Docs**
   ```
   https://your-app.vercel.app/docs
   ```

3. **Test Main App**
   ```
   https://your-app.vercel.app/
   ```
   Should redirect to: `https://your-app.vercel.app/ui/yodaai-app.html`

4. **Test Authentication**
   - Try registration
   - Try login
   - Verify JWT tokens work

5. **Test Database**
   - Create a workspace
   - Create a retrospective
   - Verify data persists

---

## 🐛 Troubleshooting

### **Issue 1: Build Timeout**

**Symptom**: Build fails with timeout error

**Solution**:
```json
// vercel.json
{
  "buildCommand": "pip install -r requirements.txt",
  "installCommand": "echo 'Using Vercel auto-install'"
}
```

Or use `requirements-prod.txt` with fewer packages.

### **Issue 2: Function Size Exceeded**

**Symptom**: Deployment fails with "Unzipped size too large"

**Solution**:
1. Remove heavy dependencies:
   - `chromadb` (unless needed)
   - `langchain` (unless needed)
   - `firebase_admin` (if not using OAuth)
   - `flask`, `django`, `tensorflow` (not used)

2. Use `requirements-prod.txt` instead

3. Split application into multiple functions (advanced)

### **Issue 3: Database Connection Errors**

**Symptom**: "Connection refused" or "timeout" errors

**Solutions**:
1. **Use pooled connection**: Add `?pgbouncer=true` to URL
2. **Check Neon firewall**: Allow Vercel IPs (usually already done)
3. **Test connection**: Use Neon SQL Editor
4. **Connection limit**: Neon free tier has limits

**Debug in Vercel**:
```python
# Add to main.py temporarily
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Issue 4: Static Files Not Serving**

**Symptom**: 404 for HTML files

**Solutions**:
1. Check `vercel.json` routes
2. Verify file paths in `app/ui/`
3. Use absolute paths in HTML files:
   ```javascript
   // Change from relative
   fetch('/api/v1/...')
   // To absolute
   fetch('https://your-app.vercel.app/api/v1/...')
   ```

Or use environment-based URLs:
```javascript
const API_BASE = window.location.origin;
fetch(`${API_BASE}/api/v1/...`)
```

### **Issue 5: CORS Errors**

**Symptom**: "Access-Control-Allow-Origin" errors

**Solution**: Update `main.py`:
```python
# For production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://www.your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Issue 6: Import Errors**

**Symptom**: "ModuleNotFoundError"

**Solutions**:
1. Check `requirements.txt` includes all needed packages
2. Verify Python version in `runtime.txt`
3. Check `.vercelignore` isn't excluding important files
4. Rebuild: `vercel --force`

### **Issue 7: Slow API Responses**

**Symptom**: First request is very slow, then fast

**Explanation**: This is **cold start** - normal for serverless

**Mitigations**:
1. Upgrade to Vercel Pro (faster cold starts)
2. Use connection pooling
3. Implement keep-alive pings
4. Use edge functions for simple endpoints

### **Issue 8: File Upload Fails**

**Symptom**: "Request too large" or "413 Payload Too Large"

**Limit**: 4.5 MB max upload on Vercel

**Solutions**:
1. **Use external storage** (S3, Cloudflare R2, etc.)
   ```python
   # Example with S3
   import boto3
   s3 = boto3.client('s3')
   s3.upload_fileobj(file, 'bucket', 'key')
   ```

2. **Compress before upload**
3. **Stream uploads** (advanced)

---

## 🔄 Alternative Deployment Options

If Vercel deployment has issues, consider these alternatives:

### **Option 1: Railway**

**Pros**: Better for Python apps, larger size limits, full VM

**Setup**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Cost**: Free tier: $5/month credit

**Best for**: Full-stack Python apps with heavy dependencies

---

### **Option 2: Render**

**Pros**: Free PostgreSQL included, Docker support, easy setup

**Setup**:
1. Create account at: https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Cost**: Free tier with limitations

**Best for**: Full applications with persistent storage

---

### **Option 3: Fly.io**

**Pros**: Global edge deployment, Docker support, generous free tier

**Setup**:
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Create app
fly launch

# Deploy
fly deploy
```

**Cost**: Free tier: 3 VMs, 3GB storage

**Best for**: Global application deployment

---

### **Option 4: DigitalOcean App Platform**

**Pros**: Simple setup, managed databases included

**Cost**: Starts at $5/month

**Best for**: Production applications with SLAs

---

## 📊 Deployment Checklist

Use this checklist before deploying:

### **Pre-Deployment**

- [ ] Database schema deployed to Neon
- [ ] All environment variables gathered
- [ ] `vercel.json` created and configured
- [ ] `requirements.txt` optimized
- [ ] `.vercelignore` created
- [ ] Static file paths verified
- [ ] CORS origins updated
- [ ] Security secrets generated

### **Deployment**

- [ ] Git repository initialized and pushed
- [ ] Vercel project created
- [ ] Environment variables added
- [ ] Build successful
- [ ] Deployment URL working

### **Post-Deployment**

- [ ] Health check passing
- [ ] Database connection working
- [ ] Authentication working
- [ ] Static files loading
- [ ] API endpoints responding
- [ ] AI features working
- [ ] Email notifications working (if enabled)
- [ ] PDF generation working
- [ ] Error handling working

---

## 📚 Additional Resources

### **Official Documentation**

- **Vercel Python**: https://vercel.com/docs/frameworks/backend/fastapi
- **Vercel Functions**: https://vercel.com/docs/functions/runtimes/python
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Neon Docs**: https://neon.tech/docs

### **Community Resources**

- **Vercel Discord**: https://vercel.com/discord
- **FastAPI Discord**: https://discord.gg/x9vGMA4qjd
- **Stack Overflow**: Tag `vercel` + `fastapi`

### **Videos**

- Deploy FastAPI to Vercel: https://www.youtube.com/watch?v=N2pxCmmh8w4
- Neon + Vercel Setup: https://neon.tech/docs/tutorials

---

## 🎯 Quick Start Commands

```bash
# 1. Create vercel.json
# (Copy content from Step 1 above)

# 2. Create runtime.txt
echo "python-3.11.0" > runtime.txt

# 3. Create .vercelignore
# (Copy content from Step 1 above)

# 4. Optimize requirements
cp requirements.txt requirements-backup.txt
# Edit requirements.txt to remove heavy packages

# 5. Deploy
vercel login
vercel

# 6. Add environment variables in Vercel dashboard
# (See Step 5 above)

# 7. Redeploy with env vars
vercel --prod

# 8. Test
curl https://your-app.vercel.app/health
```

---

## ⚡ Production Optimization Tips

### **1. Performance**

- ✅ Use Neon connection pooling (`pgbouncer=true`)
- ✅ Enable CDN caching for static files
- ✅ Use edge functions for simple endpoints
- ✅ Implement request caching where possible
- ✅ Optimize AI prompts for faster responses

### **2. Cost Management**

- ✅ Monitor OpenAI API usage
- ✅ Use caching to reduce API calls
- ✅ Optimize database queries
- ✅ Set up usage alerts in Vercel
- ✅ Consider using smaller AI models for dev

### **3. Security**

- ✅ Never commit `.env` or credentials
- ✅ Use Vercel Secrets for sensitive data
- ✅ Enable HTTPS (automatic on Vercel)
- ✅ Rotate secrets regularly
- ✅ Use strong `SECRET_KEY`

### **4. Monitoring**

- ✅ Set up Vercel Analytics
- ✅ Monitor function errors in Vercel dashboard
- ✅ Track API usage in OpenAI dashboard
- ✅ Set up Neon monitoring
- ✅ Use logging for debugging

---

## 🔐 Security Best Practices

1. **Environment Variables**
   - Use Vercel's environment variable encryption
   - Never log sensitive values
   - Rotate keys periodically

2. **Database**
   - Use SSL connections (automatic with Neon)
   - Restrict Neon IP access if possible
   - Use read-only users for certain operations

3. **API Keys**
   - Store in Vercel Secrets
   - Use different keys for dev/prod
   - Implement rate limiting

4. **Authentication**
   - Use strong SECRET_KEY (32+ characters)
   - Implement token expiration
   - Add CSRF protection for sensitive actions

---

## 📈 Scaling Considerations

### **Free Tier Limits**

| Resource | Limit | When You'll Hit It |
|----------|-------|-------------------|
| Bandwidth | 100 GB/month | ~10,000 users |
| Function Invocations | Unlimited | Never |
| Build Time | 45 min/month | Large builds |
| Team Members | 1 | Small teams |

### **When to Upgrade**

Upgrade to **Vercel Pro** ($20/month) when:
- You exceed 100 GB bandwidth
- Cold starts impact UX
- You need team collaboration
- You require advanced analytics

### **Scaling Strategies**

1. **Database**: Upgrade Neon plan for more storage/compute
2. **AI**: Optimize prompts, use caching, consider smaller models
3. **CDN**: Vercel CDN handles traffic spikes automatically
4. **Functions**: Auto-scale based on traffic

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ Health endpoint returns `{"status": "healthy"}`
✅ `/docs` Swagger UI loads
✅ Users can register and login
✅ Retrospectives can be created
✅ AI chat responds correctly
✅ Database queries work
✅ Static files load properly
✅ No console errors in browser
✅ PDF generation works
✅ Email notifications work (if enabled)

---

## 🆘 Emergency Rollback

If deployment breaks production:

```bash
# Rollback to previous deployment
vercel rollback

# Or deploy specific version
vercel --version <deployment-url>

# Check deployment history
vercel ls
```

---

## 📞 Support Resources

### **Common Issues**

- **Build fails**: Check Vercel build logs
- **Import errors**: Verify `requirements.txt`
- **Database errors**: Test in Neon SQL Editor
- **Timeout**: Increase function timeout or optimize code
- **Size limits**: Remove unused dependencies

### **Get Help**

1. **Vercel Status**: https://vercel-status.com
2. **Vercel Community**: https://github.com/vercel/vercel/discussions
3. **FastAPI Docs**: https://fastapi.tiangolo.com
4. **Neon Support**: support@neon.tech

---

**Generated**: YodaAI Vercel Deployment Guide  
**Last Updated**: 2025  
**Status**: Ready for deployment ✅

