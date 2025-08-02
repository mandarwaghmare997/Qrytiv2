# 🚀 **QRYTI PLATFORM - AWS DEPLOYMENT GUIDE**

## 📋 **OVERVIEW**

This guide provides step-by-step instructions for manually deploying the Qryti ISO 42001 AI Governance Platform to AWS from scratch. The platform consists of a React frontend and a Python Flask backend.

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Frontend:**
- **Technology:** React.js with responsive design
- **Deployment:** AWS S3 + CloudFront CDN
- **Domain:** app.qryti.com

### **Backend:**
- **Technology:** Python Flask API
- **Deployment:** AWS EC2 or AWS Lambda
- **Database:** SQLite (demo) / PostgreSQL (production)
- **Email:** Amazon SES

---

## 📦 **PREREQUISITES**

### **Required Tools:**
- AWS CLI configured with appropriate permissions
- Node.js 18+ and npm
- Python 3.11+
- Git

### **AWS Services Required:**
- S3 (Static website hosting)
- CloudFront (CDN)
- Route 53 (DNS management)
- EC2 (Backend hosting)
- SES (Email service)
- IAM (Permissions management)

### **Required Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "cloudfront:*",
        "route53:*",
        "ec2:*",
        "ses:*",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🎯 **STEP 1: CLONE AND SETUP PROJECT**

### **1.1 Clone Repository**
```bash
git clone https://github.com/your-username/Qrytiv2.git
cd Qrytiv2
```

### **1.2 Install Dependencies**

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd ../backend_simple
pip install -r requirements.txt
```

---

## 🌐 **STEP 2: FRONTEND DEPLOYMENT (S3 + CloudFront)**

### **2.1 Create S3 Bucket**
```bash
# Create bucket for static website hosting
aws s3 mb s3://app-qryti-com --region us-east-1

# Enable static website hosting
aws s3 website s3://app-qryti-com \
  --index-document index.html \
  --error-document index.html
```

### **2.2 Configure Bucket Policy**
```bash
# Create bucket policy file
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::app-qryti-com/*"
    }
  ]
}
EOF

# Apply bucket policy
aws s3api put-bucket-policy \
  --bucket app-qryti-com \
  --policy file://bucket-policy.json
```

### **2.3 Build and Deploy Frontend**
```bash
cd frontend

# Update API configuration
cat > src/config.js << EOF
const config = {
  API_BASE_URL: 'https://api.qryti.com', // Your backend URL
  APP_NAME: 'Qryti Platform',
  VERSION: '1.0.0'
};

export default config;
EOF

# Build production version
npm run build

# Deploy to S3
aws s3 sync dist/ s3://app-qryti-com --delete
```

### **2.4 Create CloudFront Distribution**
```bash
# Create CloudFront distribution
cat > cloudfront-config.json << EOF
{
  "CallerReference": "qryti-$(date +%s)",
  "Comment": "Qryti Platform CDN",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-app-qryti-com",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-app-qryti-com",
        "DomainName": "app-qryti-com.s3-website-us-east-1.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_All"
}
EOF

aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

### **2.5 Configure Custom Domain**
```bash
# Create Route 53 hosted zone (if not exists)
aws route53 create-hosted-zone \
  --name qryti.com \
  --caller-reference qryti-$(date +%s)

# Get CloudFront distribution domain name
CLOUDFRONT_DOMAIN=$(aws cloudfront list-distributions \
  --query 'DistributionList.Items[0].DomainName' \
  --output text)

# Create CNAME record
cat > route53-record.json << EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.qryti.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "$CLOUDFRONT_DOMAIN"
          }
        ]
      }
    }
  ]
}
EOF

# Get hosted zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`qryti.com.`].Id' \
  --output text | cut -d'/' -f3)

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://route53-record.json
```

---

## 🖥️ **STEP 3: BACKEND DEPLOYMENT (EC2)**

### **3.1 Launch EC2 Instance**
```bash
# Create security group
aws ec2 create-security-group \
  --group-name qryti-backend-sg \
  --description "Qryti Backend Security Group"

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
  --group-names qryti-backend-sg \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 5000 \
  --cidr 0.0.0.0/0

# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.micro \
  --key-name your-key-pair \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=qryti-backend}]'
```

### **3.2 Setup Backend on EC2**
```bash
# SSH into the instance
ssh -i your-key-pair.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python3.11 python3.11-pip git

# Clone repository
git clone https://github.com/your-username/Qrytiv2.git
cd Qrytiv2/backend_simple

# Install dependencies
pip3.11 install -r requirements.txt

# Create environment file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///qryti.db
SES_REGION=us-east-1
SES_FROM_EMAIL=no-reply@app.qryti.com
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
EOF

# Create systemd service
sudo tee /etc/systemd/system/qryti-backend.service > /dev/null << EOF
[Unit]
Description=Qryti Backend API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/Qrytiv2/backend_simple
Environment=PATH=/usr/bin
ExecStart=/usr/bin/python3.11 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start and enable service
sudo systemctl daemon-reload
sudo systemctl enable qryti-backend
sudo systemctl start qryti-backend
```

### **3.3 Configure Nginx Reverse Proxy**
```bash
# Install Nginx
sudo yum install -y nginx

# Configure Nginx
sudo tee /etc/nginx/conf.d/qryti.conf > /dev/null << EOF
server {
    listen 80;
    server_name api.qryti.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Start and enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

## 📧 **STEP 4: CONFIGURE AMAZON SES**

### **4.1 Verify Domain**
```bash
# Verify domain for SES
aws ses verify-domain-identity --domain qryti.com

# Get verification token
VERIFICATION_TOKEN=$(aws ses get-identity-verification-attributes \
  --identities qryti.com \
  --query 'VerificationAttributes."qryti.com".VerificationToken' \
  --output text)

# Add TXT record to Route 53
cat > ses-verification.json << EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "_amazonses.qryti.com",
        "Type": "TXT",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "\"$VERIFICATION_TOKEN\""
          }
        ]
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://ses-verification.json
```

### **4.2 Configure DKIM**
```bash
# Enable DKIM
aws ses put-identity-dkim-attributes \
  --identity qryti.com \
  --dkim-enabled

# Get DKIM tokens
aws ses get-identity-dkim-attributes \
  --identities qryti.com
```

---

## 🔒 **STEP 5: SSL CERTIFICATE (HTTPS)**

### **5.1 Request SSL Certificate**
```bash
# Request certificate via ACM
aws acm request-certificate \
  --domain-name qryti.com \
  --subject-alternative-names "*.qryti.com" \
  --validation-method DNS \
  --region us-east-1
```

### **5.2 Update CloudFront for HTTPS**
```bash
# Update CloudFront distribution to use SSL certificate
# (This requires manual configuration in AWS Console)
```

---

## 🧪 **STEP 6: TESTING AND VALIDATION**

### **6.1 Frontend Testing**
```bash
# Test frontend accessibility
curl -I https://app.qryti.com

# Expected: 200 OK response
```

### **6.2 Backend Testing**
```bash
# Test backend API
curl -X GET https://api.qryti.com/health

# Expected: {"status": "healthy"}
```

### **6.3 End-to-End Testing**
```bash
# Test login functionality
curl -X POST https://api.qryti.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@demo.qryti.com", "password": "demo123"}'

# Expected: JWT token response
```

---

## 🔄 **STEP 7: CONTINUOUS DEPLOYMENT**

### **7.1 Frontend Updates**
```bash
# Build and deploy frontend updates
cd frontend
npm run build
aws s3 sync dist/ s3://app-qryti-com --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --query 'DistributionList.Items[0].Id' \
  --output text)

aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

### **7.2 Backend Updates**
```bash
# SSH into EC2 instance
ssh -i your-key-pair.pem ec2-user@your-instance-ip

# Pull latest changes
cd Qrytiv2
git pull origin main

# Restart backend service
sudo systemctl restart qryti-backend
```

---

## 📊 **STEP 8: MONITORING AND MAINTENANCE**

### **8.1 CloudWatch Monitoring**
```bash
# Create CloudWatch alarms for EC2 instance
aws cloudwatch put-metric-alarm \
  --alarm-name "qryti-backend-cpu" \
  --alarm-description "High CPU usage" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### **8.2 Log Management**
```bash
# View backend logs
sudo journalctl -u qryti-backend -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**

#### **Frontend not loading:**
1. Check S3 bucket policy
2. Verify CloudFront distribution status
3. Check DNS propagation

#### **Backend API errors:**
1. Check EC2 instance status
2. Verify security group rules
3. Check backend service logs

#### **CORS errors:**
1. Verify backend CORS configuration
2. Check API endpoint URLs in frontend config

#### **Email not sending:**
1. Verify SES domain verification
2. Check AWS credentials
3. Verify SES sending limits

---

## 📝 **ENVIRONMENT VARIABLES**

### **Frontend (.env)**
```bash
REACT_APP_API_URL=https://api.qryti.com
REACT_APP_APP_NAME=Qryti Platform
REACT_APP_VERSION=1.0.0
```

### **Backend (.env)**
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///qryti.db
SES_REGION=us-east-1
SES_FROM_EMAIL=no-reply@app.qryti.com
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
CORS_ORIGINS=https://app.qryti.com
```

---

## 💰 **COST ESTIMATION**

### **Monthly AWS Costs (Approximate):**
- **S3:** $1-5 (depending on traffic)
- **CloudFront:** $1-10 (depending on traffic)
- **EC2 t3.micro:** $8-10
- **Route 53:** $0.50 per hosted zone
- **SES:** $0.10 per 1,000 emails
- **Total:** ~$15-30/month

---

## 🔐 **SECURITY BEST PRACTICES**

1. **Use IAM roles** instead of access keys when possible
2. **Enable MFA** for AWS root account
3. **Regularly rotate** access keys and secrets
4. **Use HTTPS** for all communications
5. **Keep dependencies** updated
6. **Monitor logs** for suspicious activity
7. **Use AWS WAF** for additional protection

---

## 📞 **SUPPORT**

For deployment issues or questions:
- **Email:** support@qryti.com
- **Documentation:** https://docs.qryti.com
- **GitHub Issues:** https://github.com/your-username/Qrytiv2/issues

---

## 📄 **LICENSE**

This deployment guide is part of the Qryti Platform project. Please refer to the main project license for usage terms.

---

**Last Updated:** January 2024  
**Version:** 1.0.0  
**Maintained by:** Qryti Development Team

