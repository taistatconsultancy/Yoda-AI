# 🚀 YodaAI Deployment Quick Guide

**Quick reference for deploying YodaAI to production**

---

## 📦 What You Need

✅ **Vercel account** (https://vercel.com)  
✅ **Neon PostgreSQL** (https://neon.tech)  
✅ **OpenAI API key** (https://platform.openai.com)  
✅ **Git repository** with your code

---

## ⚡ Quick Start (5 Steps)

### 1️⃣ Setup Files

The following files have been created for you:

- ✅ `vercel.json` - Vercel configuration
- ✅ `runtime.txt` - Python version
- ✅ `.vercelignore` - Exclude unnecessary files
- ✅ `requirements-prod.txt` - Optimized dependencies
- ✅ `app/database/database.py` - Serverless-aware connection pooling

### 2️⃣ Initialize Git

```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin <your-repo-url>
git push -u origin main
```

### 3️⃣ Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel
```

### 4️⃣ Configure Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables, add:

**Required:**
```
NEON_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
OPENAI_API_KEY=sk-your-key
SECRET_KEY=<generate with: openssl rand -hex 32>
USE_LOCAL_DB=False
```

**Recommended:**
```
DEBUG=False
ENVIRONMENT=production
APP_URL=https://your-app.vercel.app
```

### 5️⃣ Redeploy

```bash
vercel --prod
```

---

## 🔧 Configuration Files

### `vercel.json`
- Configures Python runtime
- Routes API and static files
- Sets max function duration to 60s

### `runtime.txt`
- Python 3.11.0 (required by Vercel)

### `.vercelignore`
- Excludes dev files, docs, test files
- Reduces deployment size

### `requirements-prod.txt`
- Minimal production dependencies
- Removes dev-only packages

---

## 🗄️ Database Setup

### Neon PostgreSQL

1. **Create project** in Neon Console
2. **Run migrations** using SQL Editor
3. **Copy connection string**
4. **Add to Vercel** environment variables

**Important**: Use pooled connection for serverless!

```
NEON_DATABASE_URL=postgresql://...?sslmode=require&pgbouncer=true
```

### Schema Deployment

**Option 1: SQL Editor** (Recommended)
1. Open Neon SQL Editor
2. Paste database schema SQL
3. Run all statements

**Option 2: Alembic**
```bash
alembic upgrade head
```

---

## 🔐 Security Checklist

- [ ] Generated strong `SECRET_KEY`
- [ ] Added all environment variables
- [ ] Never committed `.env` file
- [ ] Set `DEBUG=False` in production
- [ ] Enabled SSL for database
- [ ] Configured CORS correctly

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Build timeout | Use `requirements-prod.txt` |
| Function too large | Remove `chromadb`, `langchain` |
| Database errors | Use `pgbouncer=true` |
| Import errors | Check `requirements.txt` |
| Slow cold starts | Normal for serverless |

---

## 📊 Testing Your Deployment

```bash
# Health check
curl https://your-app.vercel.app/health

# API docs
open https://your-app.vercel.app/docs

# Main app
open https://your-app.vercel.app
```

---

## 📚 Full Documentation

For detailed deployment instructions, troubleshooting, and best practices, see:

📖 **[VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md)**

This comprehensive guide includes:
- Detailed architecture explanation
- Step-by-step deployment walkthrough
- Database configuration
- Environment variable reference
- Troubleshooting guide
- Alternative deployment options
- Production optimization tips

---

## 🆘 Need Help?

**Vercel**: https://vercel.com/docs  
**Neon**: https://neon.tech/docs  
**FastAPI**: https://fastapi.tiangolo.com  
**Support**: Check deployment logs in Vercel dashboard

---

## ✅ Deployment Checklist

- [ ] Git repository ready
- [ ] Vercel project created
- [ ] Environment variables configured
- [ ] Database schema deployed
- [ ] Build successful
- [ ] Health check passing
- [ ] API endpoints working
- [ ] Frontend loading
- [ ] Authentication working
- [ ] AI features functional

---

**Ready to deploy!** 🚀

Follow the 5 quick steps above, or read the full guide for detailed instructions.

