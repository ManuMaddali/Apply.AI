# 🚀 Apply.AI Production Deployment Guide

## 📋 **Pre-Deployment Checklist**

### 1. **Environment Preparation**
```bash
# Create production environment files
cp .env.example .env.production
cp backend/.env.example backend/.env.production
```

### 2. **Database Setup**
```bash
# Set up PostgreSQL production database
DATABASE_URL=postgresql://user:password@host:5432/applyai_prod
```

### 3. **Security Configuration**
```bash
# Generate secure secrets
NEXTAUTH_SECRET=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)
```

## 🎯 **Option A: Vercel + Railway Deployment**

### **Frontend Deployment (Vercel)**

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Configure Frontend for Production**
```bash
cd frontend
npm run build
```

3. **Deploy to Vercel**
```bash
vercel --prod
```

4. **Configure Environment Variables**
```bash
# In Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_ENV=production
```

### **Backend Deployment (Railway)**

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and Initialize**
```bash
railway login
cd backend
railway init
```

3. **Configure Environment Variables**
```bash
railway variables set NODE_ENV=production
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set OPENAI_API_KEY=$OPENAI_API_KEY
railway variables set CORS_ORIGIN=https://your-frontend.vercel.app
```

4. **Deploy Backend**
```bash
railway up
```

5. **Set up Database**
```bash
# Add PostgreSQL service in Railway dashboard
railway add postgresql
railway variables set DATABASE_URL=$RAILWAY_POSTGRESQL_URL
```

## 🏗️ **Option B: AWS Deployment**

### **1. Infrastructure Setup**

**Create VPC and Security Groups:**
```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-security-group --group-name applyai-sg --description "Apply.AI Security Group"
```

**Set up RDS Database:**
```bash
aws rds create-db-instance \
  --db-instance-identifier applyai-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password $DB_PASSWORD \
  --allocated-storage 20
```

### **2. Backend Deployment (ECS)**

**Create Dockerfile for Production:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8000
CMD ["npm", "start"]
```

**Deploy to ECS:**
```bash
# Build and push to ECR
aws ecr create-repository --repository-name applyai-backend
docker build -t applyai-backend .
docker tag applyai-backend:latest $ECR_URI/applyai-backend:latest
docker push $ECR_URI/applyai-backend:latest

# Create ECS service
aws ecs create-service \
  --cluster applyai-cluster \
  --service-name applyai-backend \
  --task-definition applyai-backend \
  --desired-count 1
```

### **3. Frontend Deployment (S3 + CloudFront)**

```bash
# Build frontend
cd frontend
npm run build

# Deploy to S3
aws s3 sync out/ s3://applyai-frontend --delete

# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

## 🌍 **Domain and SSL Configuration**

### **Custom Domain Setup**

1. **Purchase Domain** (alternatives to apply.ai):
   - applyai.io
   - resumeai.com
   - tailormyresume.com
   - airesume.app

2. **Configure DNS:**
```bash
# For Vercel
CNAME www your-app.vercel.app
A @ 76.76.19.61

# For Railway
CNAME api your-backend.railway.app
```

3. **SSL Certificates:**
```bash
# Automatic with Vercel/Railway
# Manual with AWS Certificate Manager
aws acm request-certificate \
  --domain-name yourdomain.com \
  --validation-method DNS
```

## 📊 **Monitoring Setup**

### **1. Application Monitoring**
```bash
# Install Sentry
npm install @sentry/nextjs @sentry/node

# Configure Sentry
SENTRY_DSN=your_sentry_dsn
SENTRY_ORG=your_org
SENTRY_PROJECT=applyai
```

### **2. Performance Monitoring**
```bash
# Add performance tracking
NEXT_PUBLIC_VERCEL_ANALYTICS_ID=your_analytics_id

# Database monitoring
POSTGRES_MONITOR=true
SLOW_QUERY_LOG=true
```

### **3. Log Management**
```bash
# Centralized logging
LOG_LEVEL=info
LOG_FORMAT=json
LOG_DESTINATION=cloudwatch
```

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Workflow**
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd frontend && npm ci && npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd backend && npm ci
      - uses: railway/action@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 🎯 **Production Environment Variables**

### **Frontend (.env.production)**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### **Backend (.env.production)**
```bash
NODE_ENV=production
PORT=8000
DATABASE_URL=postgresql://user:pass@host:5432/db
OPENAI_API_KEY=your_openai_key
CORS_ORIGIN=https://yourdomain.com
RATE_LIMIT=10
SESSION_SECRET=secure_random_string
UPLOAD_MAX_SIZE=10485760
FILE_RETENTION_DAYS=30
SENTRY_DSN=your_sentry_dsn
```

## 🔍 **Post-Deployment Testing**

### **1. Health Checks**
```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend accessibility
curl -I https://yourdomain.com

# Database connectivity
psql $DATABASE_URL -c "SELECT 1;"
```

### **2. Load Testing**
```bash
# Install artillery
npm install -g artillery

# Run load test
artillery quick --count 10 --num 2 https://api.yourdomain.com/health
```

### **3. Security Testing**
```bash
# SSL Labs test
https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

# Security headers
curl -I https://yourdomain.com
```

## 📈 **Scaling Considerations**

### **Auto-scaling Configuration**
```bash
# Railway auto-scaling
RAILWAY_AUTOSCALE_MIN=1
RAILWAY_AUTOSCALE_MAX=10
RAILWAY_AUTOSCALE_TARGET_CPU=70

# AWS auto-scaling
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name applyai-asg \
  --min-size 1 \
  --max-size 10 \
  --desired-capacity 2
```

### **Database Scaling**
```bash
# Read replicas for heavy read workloads
aws rds create-db-instance-read-replica \
  --db-instance-identifier applyai-db-replica \
  --source-db-instance-identifier applyai-db

# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_CONNECTIONS=100
```

## 💰 **Cost Optimization**

### **1. Monitoring Costs**
```bash
# AWS Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Railway usage tracking
railway usage
```

### **2. Optimization Strategies**
- Use CDN for static assets
- Implement response caching
- Optimize database queries
- Use appropriate instance sizes
- Set up automated shutdowns for dev environments

## 🎯 **Go-Live Checklist**

- [ ] Domain configured and SSL active
- [ ] All environment variables set
- [ ] Database migrations completed
- [ ] Security headers configured
- [ ] Monitoring and alerting active
- [ ] Backup strategy implemented
- [ ] Legal pages (Privacy Policy, Terms) deployed
- [ ] Error tracking operational
- [ ] Performance monitoring active
- [ ] Load testing completed
- [ ] Security audit passed 