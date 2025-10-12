# YodaAI Vercel Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
- Vercel CLI installed: `npm i -g vercel`
- Vercel account with API key (PAT) configured

### Step 1: Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### Step 2: Deploy to Vercel
```bash
vercel --prod
```

### Step 3: Set Environment Variables
In your Vercel dashboard, go to Settings > Environment Variables and add:

```
DATABASE_URL=sqlite:///./yodaai.db
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
```

## 📁 Project Structure for Vercel

```
├── api/
│   └── index.py          # Vercel serverless function entry point
├── app/                  # FastAPI application
├── yodaai-enhanced.html  # Main UI (served as static file)
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies
└── .vercelignore       # Files to ignore during deployment
```

## 🔧 Configuration Files

### vercel.json
- Routes API calls to `/api/index.py`
- Serves `yodaai-enhanced.html` as the main page
- Sets up environment variables
- Configures serverless function timeout

### api/index.py
- Entry point for Vercel serverless functions
- Imports the FastAPI app from `main.py`

## 🌐 URLs After Deployment

- **Main App**: `https://your-project.vercel.app/`
- **API**: `https://your-project.vercel.app/api/`
- **API Docs**: `https://your-project.vercel.app/docs`

## 🛠️ Local Development

### Option 1: Standalone HTML
```bash
# Open yodaai-enhanced.html in browser
open yodaai-enhanced.html
```

### Option 2: Full Backend
```bash
py start_server.py
# Visit http://localhost:8000
```

## 🔍 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: pydantic_settings**
   ```bash
   py -m pip install pydantic-settings
   ```

2. **Database Connection Issues**
   - Ensure DATABASE_URL is set correctly
   - For production, use PostgreSQL or similar

3. **Environment Variables**
   - Check Vercel dashboard for correct env vars
   - Ensure all required variables are set

### Deployment Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] vercel.json properly configured
- [ ] API entry point created
- [ ] Static files properly routed
- [ ] Database connection working
- [ ] Authentication working
- [ ] UI accessible

## 📊 Performance Optimization

- Static files served via CDN
- API routes optimized for serverless
- Database connections pooled
- Caching enabled where appropriate

## 🔒 Security

- Environment variables encrypted
- API keys secured
- Authentication tokens properly handled
- CORS configured correctly

## 📈 Monitoring

- Vercel Analytics enabled
- Error tracking configured
- Performance monitoring active
- Logs accessible via Vercel dashboard

