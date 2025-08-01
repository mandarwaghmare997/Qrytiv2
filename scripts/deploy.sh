#!/bin/bash

# Qrytiv2 Deployment Script
# Usage: ./scripts/deploy.sh [environment] [component]
# Example: ./scripts/deploy.sh production frontend

set -e  # Exit on any error

# Configuration
AWS_REGION="ap-south-1"
S3_BUCKET_PROD="app.qryti.com"
S3_BUCKET_STAGING="qrytiv2-staging"
CLOUDFRONT_DISTRIBUTION_ID="E2HCV8NIH27XPX"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
ENVIRONMENT=${1:-staging}
COMPONENT=${2:-all}

log_info "Starting deployment to $ENVIRONMENT environment"
log_info "Component: $COMPONENT"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Set S3 bucket based on environment
if [[ "$ENVIRONMENT" == "production" ]]; then
    S3_BUCKET=$S3_BUCKET_PROD
    WEBSITE_URL="https://app.qryti.com"
else
    S3_BUCKET=$S3_BUCKET_STAGING
    WEBSITE_URL="http://$S3_BUCKET_STAGING.s3-website.$AWS_REGION.amazonaws.com"
fi

# Deploy frontend
deploy_frontend() {
    log_info "Deploying frontend to $ENVIRONMENT"
    
    # Check if frontend directory exists
    if [[ ! -d "frontend" ]]; then
        log_error "Frontend directory not found"
        return 1
    fi
    
    # Install dependencies and build
    cd frontend
    log_info "Installing frontend dependencies..."
    npm install -g pnpm
    pnpm install
    
    log_info "Building frontend..."
    pnpm build
    
    # Deploy to S3
    log_info "Uploading to S3 bucket: $S3_BUCKET"
    aws s3 sync dist/ s3://$S3_BUCKET/ --delete --region $AWS_REGION
    
    # Invalidate CloudFront cache for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "Invalidating CloudFront cache..."
        aws cloudfront create-invalidation \
            --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
            --paths "/*" \
            --region $AWS_REGION
    fi
    
    cd ..
    log_success "Frontend deployed successfully to $WEBSITE_URL"
}

# Deploy backend
deploy_backend() {
    log_info "Deploying backend to $ENVIRONMENT"
    
    # Check if backend directory exists
    if [[ ! -d "backend" ]]; then
        log_error "Backend directory not found"
        return 1
    fi
    
    # Install dependencies
    log_info "Installing backend dependencies..."
    cd backend
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    # TODO: Add actual backend deployment logic
    # This could include:
    # - Creating Lambda deployment package
    # - Updating Lambda function
    # - Updating API Gateway
    # - Database migrations
    
    log_warning "Backend deployment logic not yet implemented"
    log_info "Backend deployment would happen here for $ENVIRONMENT"
    
    cd ..
    log_success "Backend deployment completed"
}

# Health check
health_check() {
    log_info "Running health check..."
    
    # Wait a bit for deployment to propagate
    sleep 10
    
    # Check website health
    response=$(curl -s -o /dev/null -w "%{http_code}" $WEBSITE_URL)
    if [[ $response -eq 200 ]]; then
        log_success "Health check passed (HTTP $response)"
    else
        log_error "Health check failed (HTTP $response)"
        return 1
    fi
}

# Main deployment logic
main() {
    # Check AWS CLI is configured
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        log_error "AWS CLI not configured or credentials invalid"
        exit 1
    fi
    
    log_info "AWS credentials verified"
    
    # Deploy based on component
    case $COMPONENT in
        "frontend")
            deploy_frontend
            ;;
        "backend")
            deploy_backend
            ;;
        "all")
            deploy_frontend
            deploy_backend
            ;;
        *)
            log_error "Invalid component. Use 'frontend', 'backend', or 'all'"
            exit 1
            ;;
    esac
    
    # Run health check
    if [[ "$COMPONENT" == "frontend" || "$COMPONENT" == "all" ]]; then
        health_check
    fi
    
    log_success "Deployment completed successfully!"
    log_info "Website URL: $WEBSITE_URL"
    log_info "Deployment time: $(date)"
}

# Run main function
main

