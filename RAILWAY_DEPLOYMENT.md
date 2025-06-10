# Railway Deployment Guide

This guide walks you through deploying the MuscleFormAnalyzer FastAPI backend to Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install via npm
   ```bash
   npm install -g @railway/cli
   ```
3. **Firebase Project**: Set up Firebase Authentication
4. **Git Repository**: Code pushed to GitHub/GitLab

## 🚀 Quick Deploy

### Option 1: Automated Script
```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Steps

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Initialize Project**
   ```bash
   cd backend
   railway init
   ```

3. **Add PostgreSQL Database**
   ```bash
   railway add --database postgresql
   ```

4. **Deploy**
   ```bash
   railway up
   ```

## ⚙️ Environment Configuration

Set these environment variables in Railway dashboard:

### Required Variables
```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Database (automatically set by Railway)
DATABASE_URL=postgresql://...

# Security
SECRET_KEY=your-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Firebase
FIREBASE_CREDENTIALS={"type":"service_account",...}
FIREBASE_PROJECT_ID=your-firebase-project-id

# CORS & Hosts
CORS_ORIGINS=https://muscle-form-analyzer.vercel.app,https://muscle-form-analyzer-*.vercel.app
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
```

### Optional Variables
```bash
# MediaPipe Settings
MEDIAPIPE_MODEL_COMPLEXITY=1
MEDIAPIPE_MIN_DETECTION_CONFIDENCE=0.7
MEDIAPIPE_MIN_TRACKING_CONFIDENCE=0.7

# File Upload
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=INFO
```

## 🗄️ Database Migration

### From SQLite to PostgreSQL

1. **Export SQLite Data** (if you have existing data)
   ```bash
   python scripts/export_sqlite_data.py
   ```

2. **Railway will automatically create tables** on first deployment

3. **Import Data** (if needed)
   ```bash
   python scripts/import_to_postgresql.py
   ```

## 🔧 Configuration Files

### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### `Dockerfile`
- Multi-stage build for optimization
- Python 3.11 slim base image
- Non-root user for security
- Health check endpoints
- MediaPipe and OpenCV dependencies

## 🔗 API Endpoints

Once deployed, your API will be available at:
- **Base URL**: `https://your-app.railway.app`
- **Health Check**: `/health`
- **API Documentation**: `/docs`
- **Authentication**: `/api/auth/*`
- **Form Analysis**: `/api/form/*`
- **Nutrition**: `/api/nutrition/*`
- **Progress**: `/api/progress/*`

## 📱 Frontend Integration

Update your frontend environment variables:

```bash
# Vercel/Next.js
NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app

# React
REACT_APP_API_BASE_URL=https://your-app.railway.app
```

## 🏥 Health Monitoring

### Built-in Health Checks
- `/health` - Comprehensive health status
- `/ready` - Readiness probe for Railway
- Automatic database connection testing

### Monitoring Setup
```bash
# View logs
railway logs

# Monitor deployment
railway status

# View metrics
railway metrics
```

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for version conflicts
   - Verify Dockerfile syntax
   - Ensure all dependencies are listed

2. **Database Connection Issues**
   - Verify DATABASE_URL is set
   - Check PostgreSQL service is running
   - Review network security groups

3. **MediaPipe/OpenCV Issues**
   - System dependencies included in Dockerfile
   - Use headless OpenCV version
   - Check memory limits

4. **Firebase Authentication Issues**
   - Verify FIREBASE_CREDENTIALS format
   - Check project ID matches
   - Ensure service account has proper permissions

### Debug Commands
```bash
# View deployment logs
railway logs --tail

# SSH into container (if needed)
railway shell

# Check environment variables
railway variables

# Restart service
railway restart
```

## 📊 Performance Optimization

### Resource Limits
```json
{
  "deploy": {
    "numReplicas": 1,
    "resources": {
      "memory": "2Gi",
      "cpu": "1000m"
    }
  }
}
```

### Caching Strategy
- Redis for session storage
- Database query optimization
- MediaPipe model caching

## 🔐 Security Best Practices

1. **Environment Variables**
   - Never commit secrets to git
   - Use Railway's secret management
   - Rotate keys regularly

2. **Network Security**
   - Configure CORS properly
   - Use HTTPS only
   - Implement rate limiting

3. **Database Security**
   - Use connection pooling
   - Enable SSL connections
   - Regular security updates

## 🔄 CI/CD Pipeline

### GitHub Actions Integration
```yaml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up --service backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Increase replica count in railway.json
- Use external Redis for session storage
- Implement database read replicas

### Vertical Scaling
- Monitor memory usage for MediaPipe
- Adjust CPU limits for video processing
- Consider GPU instances for AI workloads

## 💡 Tips & Best Practices

1. **Development Workflow**
   - Use staging environment for testing
   - Implement feature flags
   - Monitor deployment metrics

2. **Cost Optimization**
   - Use appropriate resource limits
   - Implement auto-scaling
   - Monitor usage patterns

3. **Maintenance**
   - Regular dependency updates
   - Database maintenance windows
   - Log rotation and cleanup

## 📞 Support

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **MediaPipe Documentation**: [mediapipe.dev](https://mediapipe.dev)

---

🎉 **Congratulations!** Your MuscleFormAnalyzer backend is now running on Railway with enterprise-grade infrastructure, automatic scaling, and monitoring capabilities.