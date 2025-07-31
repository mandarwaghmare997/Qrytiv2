# AWS Deployment Configuration

## S3 Bucket: app.qryti.com
- Region: ap-south-1 (Mumbai)
- Website Endpoint: http://app.qryti.com.s3-website.ap-south-1.amazonaws.com
- Custom Domain: app.qryti.com (Route 53 configured)

## Deployment Commands:
```bash
# Build React app
cd frontend && pnpm run build

# Deploy to S3
aws s3 sync dist/ s3://app.qryti.com --delete --region ap-south-1
```

## Status: ✅ DEPLOYED
- Frontend successfully deployed to AWS S3
- Static website hosting enabled
- Public access configured
- Ready for Route 53 DNS resolution

Deployed by: Qryti Dev Team
Date: Thu Jul 31 08:50:39 EDT 2025

