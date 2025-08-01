# Qrytiv2 CI/CD Pipeline Architecture

## Current Infrastructure Analysis

### **Existing Setup:**
- **GitHub Repository:** https://github.com/mandarwaghmare997/Qrytiv2
- **AWS Region:** ap-south-1 (Mumbai)
- **S3 Buckets:** 
  - `app.qryti.com` (production website)
  - `qrytiv2-frontend` (backup/staging)
- **CloudFront Distribution:** E2HCV8NIH27XPX (serving app.qryti.com)
- **SSL Certificate:** ACM certificate for app.qryti.com
- **Route 53:** DNS configured for app.qryti.com

### **Project Structure:**
```
Qrytiv2/
├── frontend/          # React + Vite application
├── backend/           # FastAPI Python application  
├── fullstack/         # Combined Flask application
└── .github/           # GitHub Actions workflows (to be created)
```

## CI/CD Pipeline Design

### **Pipeline Objectives:**
1. **Automated Testing:** Run tests on every push/PR
2. **Automated Building:** Build frontend and backend applications
3. **Automated Deployment:** Deploy to AWS on successful builds
4. **Environment Management:** Support for staging and production
5. **Cost Optimization:** Stay within AWS Free Tier limits

### **Pipeline Architecture:**

#### **1. GitHub Actions Workflows:**

##### **Frontend Pipeline (`frontend-deploy.yml`):**
```yaml
Trigger: Push to main branch (frontend/ changes)
Steps:
1. Checkout code
2. Setup Node.js 20
3. Install dependencies (pnpm)
4. Run tests (if any)
5. Build production bundle
6. Deploy to S3 bucket (app.qryti.com)
7. Invalidate CloudFront cache
8. Notify deployment status
```

##### **Backend Pipeline (`backend-deploy.yml`):**
```yaml
Trigger: Push to main branch (backend/ changes)
Steps:
1. Checkout code
2. Setup Python 3.11
3. Install dependencies
4. Run tests (pytest)
5. Build Docker image (optional)
6. Deploy to AWS (ECS/Lambda/EC2)
7. Update API endpoints
8. Run health checks
```

##### **Full Integration Pipeline (`integration-deploy.yml`):**
```yaml
Trigger: Manual dispatch or release tags
Steps:
1. Run frontend pipeline
2. Run backend pipeline
3. Integration testing
4. Production deployment
5. Smoke tests
6. Rollback on failure
```

#### **2. AWS Services Integration:**

##### **Frontend Deployment:**
- **S3:** Static website hosting
- **CloudFront:** Global CDN with SSL
- **Route 53:** DNS management
- **IAM:** Deployment permissions

##### **Backend Deployment Options:**
1. **AWS Lambda + API Gateway** (Recommended - Free Tier)
   - Serverless FastAPI deployment
   - Auto-scaling
   - Pay-per-request pricing

2. **ECS Fargate** (Alternative)
   - Containerized deployment
   - Managed container service
   - Predictable pricing

3. **EC2 + Docker** (Development)
   - Full control
   - Cost-effective for development

#### **3. Environment Strategy:**

##### **Staging Environment:**
- **S3 Bucket:** `staging.qryti.com` or `qrytiv2-staging`
- **CloudFront:** Separate distribution
- **Database:** Separate RDS instance (or SQLite for development)
- **API:** Staging Lambda functions

##### **Production Environment:**
- **S3 Bucket:** `app.qryti.com` (existing)
- **CloudFront:** E2HCV8NIH27XPX (existing)
- **Database:** Production RDS instance
- **API:** Production Lambda functions

### **Security & Best Practices:**

#### **GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_NAME`
- `CLOUDFRONT_DISTRIBUTION_ID`

#### **IAM Permissions:**
- S3 bucket read/write
- CloudFront invalidation
- Lambda deployment
- ECS deployment (if used)
- RDS access (for backend)

#### **Monitoring & Alerts:**
- CloudWatch logs
- GitHub Actions notifications
- Slack/email alerts on failures
- Performance monitoring

### **Cost Optimization:**

#### **AWS Free Tier Usage:**
- **S3:** 5GB storage, 20,000 GET requests
- **CloudFront:** 1TB data transfer, 10M requests
- **Lambda:** 1M requests, 400,000 GB-seconds
- **API Gateway:** 1M API calls
- **RDS:** 750 hours micro instance

#### **Cost-Saving Strategies:**
- Use Lambda for backend (pay-per-request)
- Optimize CloudFront caching
- Compress static assets
- Use S3 lifecycle policies
- Monitor usage with CloudWatch

### **Deployment Flow:**

#### **Development Workflow:**
1. Developer pushes code to feature branch
2. GitHub Actions runs tests and builds
3. Creates preview deployment (optional)
4. Code review and approval
5. Merge to main branch
6. Automatic deployment to staging
7. Manual promotion to production

#### **Rollback Strategy:**
1. Keep previous deployment artifacts
2. CloudFront cache invalidation
3. Database migration rollback scripts
4. Automated health checks
5. Quick rollback commands

### **Implementation Phases:**

#### **Phase 1: Basic Frontend CI/CD**
- Setup GitHub Actions for frontend
- Automate S3 deployment
- CloudFront invalidation

#### **Phase 2: Backend CI/CD**
- Setup backend testing
- Lambda deployment automation
- API Gateway configuration

#### **Phase 3: Integration & Testing**
- End-to-end testing
- Staging environment setup
- Production deployment automation

#### **Phase 4: Monitoring & Optimization**
- CloudWatch integration
- Performance monitoring
- Cost optimization
- Alert setup

### **Success Metrics:**
- **Deployment Time:** < 5 minutes for frontend, < 10 minutes for backend
- **Success Rate:** > 95% successful deployments
- **Rollback Time:** < 2 minutes
- **Cost:** Stay within AWS Free Tier limits
- **Uptime:** > 99.9% availability

This architecture ensures reliable, fast, and cost-effective CI/CD pipeline for the Qrytiv2 project while maintaining professional deployment standards.

