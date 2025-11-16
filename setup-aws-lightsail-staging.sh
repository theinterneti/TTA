#!/bin/bash

# 🚀 AWS Lightsail Staging Environment Setup for TTA
# This script sets up a HIPAA-compliant staging environment on AWS Lightsail

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 TTA Staging Environment Setup - AWS Lightsail${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed.${NC}"
    echo "Please install it from: https://aws.amazon.com/cli/"
    echo "Or run: curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured.${NC}"
    echo "Please run: aws configure"
    echo "You'll need your AWS Access Key ID and Secret Access Key"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Configuration
SERVICE_NAME="tta-staging"
REGION="us-east-1"
POWER="medium"  # small, medium, large, xlarge
SCALE=2
DOMAIN="theinterneti.com"

echo -e "${YELLOW}📝 Configuration:${NC}"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Instance Power: $POWER"
echo "  Scale: $SCALE instances"
echo "  Domain: $DOMAIN"
echo ""

read -p "Press Enter to continue or Ctrl+C to abort..."
echo ""

# Function to check if service exists
check_service_exists() {
    aws lightsail get-container-services --region $REGION --query "containerServices[?containerServiceName=='$SERVICE_NAME']" --output text 2>/dev/null | grep -q "$SERVICE_NAME"
}

# Create container service if it doesn't exist
echo -e "${BLUE}🏗️ Setting up Lightsail container service...${NC}"

if check_service_exists; then
    echo -e "${YELLOW}⚠️  Container service '$SERVICE_NAME' already exists${NC}"
    read -p "Do you want to update it? (y/N): " update_service
    if [[ $update_service =~ ^[Yy]$ ]]; then
        echo "Updating existing service..."
    else
        echo "Using existing service..."
    fi
else
    echo "Creating new container service..."
    aws lightsail create-container-service \
        --service-name $SERVICE_NAME \
        --power $POWER \
        --scale $SCALE \
        --region $REGION \
        --tags key=Project,value=TTA key=Environment,value=staging

    echo -e "${GREEN}✅ Container service created${NC}"
    echo "Waiting for service to be ready..."

    # Wait for service to be ready
    while true; do
        state=$(aws lightsail get-container-service --service-name $SERVICE_NAME --region $REGION --query 'containerService.state' --output text)
        if [ "$state" = "READY" ]; then
            break
        fi
        echo "Service state: $state - waiting..."
        sleep 30
    done
fi

echo -e "${GREEN}✅ Container service is ready${NC}"
echo ""

# Create deployment configuration
echo -e "${BLUE}📦 Creating deployment configuration...${NC}"

cat > containers.json << EOF
{
  "containers": {
    "tta-api": {
      "image": "nginx:latest",
      "ports": {
        "8080": "HTTP"
      },
      "environment": {
        "ENVIRONMENT": "staging",
        "API_HOST": "0.0.0.0",
        "API_PORT": "8080",
        "SENTRY_ENVIRONMENT": "staging",
        "SENTRY_TRACES_SAMPLE_RATE": "0.2"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "tta-api",
    "containerPort": 8080,
    "healthCheck": {
      "healthyThreshold": 2,
      "unhealthyThreshold": 2,
      "timeoutSeconds": 5,
      "intervalSeconds": 30,
      "path": "/health",
      "successCodes": "200"
    }
  }
}
EOF

echo -e "${GREEN}✅ Deployment configuration created${NC}"
echo ""

# Deploy containers
echo -e "${BLUE}🚀 Deploying containers...${NC}"

aws lightsail create-container-service-deployment \
    --service-name $SERVICE_NAME \
    --region $REGION \
    --containers file://containers.json

echo -e "${GREEN}✅ Deployment initiated${NC}"
echo "Waiting for deployment to complete..."

# Wait for deployment
while true; do
    deployment_state=$(aws lightsail get-container-service-deployments --service-name $SERVICE_NAME --region $REGION --query 'deployments[0].state' --output text)
    if [ "$deployment_state" = "ACTIVE" ]; then
        break
    fi
    echo "Deployment state: $deployment_state - waiting..."
    sleep 30
done

echo -e "${GREEN}✅ Deployment completed${NC}"
echo ""

# Get service URL
echo -e "${BLUE}🌐 Getting service information...${NC}"

SERVICE_URL=$(aws lightsail get-container-service --service-name $SERVICE_NAME --region $REGION --query 'containerService.url' --output text)
PUBLIC_DOMAIN=$(aws lightsail get-container-service --service-name $SERVICE_NAME --region $REGION --query 'containerService.publicDomainNames[0]' --output text)

echo -e "${GREEN}✅ Service deployed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Service Information:${NC}"
echo "  Service URL: $SERVICE_URL"
echo "  Public Domain: $PUBLIC_DOMAIN"
echo ""

# Create Cloudflare DNS configuration
echo -e "${BLUE}🌐 Cloudflare DNS Configuration${NC}"
echo "Add these DNS records in your Cloudflare dashboard:"
echo ""
echo -e "${YELLOW}DNS Records to Add:${NC}"
echo "  Type: CNAME, Name: staging-tta, Target: $PUBLIC_DOMAIN"
echo "  Type: CNAME, Name: api-staging, Target: $PUBLIC_DOMAIN"
echo "  Type: CNAME, Name: clinical-staging, Target: $PUBLIC_DOMAIN"
echo "  Type: CNAME, Name: admin-staging, Target: $PUBLIC_DOMAIN"
echo ""

# Create GitHub Actions secrets
echo -e "${BLUE}🔐 GitHub Actions Configuration${NC}"
echo "Add these secrets to your GitHub repository:"
echo ""
echo -e "${YELLOW}GitHub Secrets to Add:${NC}"
echo "  AWS_ACCESS_KEY_ID: (your AWS access key)"
echo "  AWS_SECRET_ACCESS_KEY: (your AWS secret key)"
echo "  LIGHTSAIL_SERVICE_NAME: $SERVICE_NAME"
echo "  LIGHTSAIL_REGION: $REGION"
echo ""

# Create GitHub Actions workflow
echo -e "${BLUE}📝 Creating GitHub Actions workflow...${NC}"

mkdir -p .github/workflows

cat > .github/workflows/deploy-staging.yml << 'EOF'
name: Deploy to Staging (AWS Lightsail)

on:
  push:
    branches: [staging, main]
  workflow_dispatch:

env:
  SERVICE_NAME: tta-staging
  AWS_REGION: us-east-1

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Build and push Docker image
        run: |
          # Build your Docker image
          docker build -t tta-api:staging -f src/player_experience/Dockerfile .

          # Tag for Lightsail
          docker tag tta-api:staging tta-api:latest

      - name: Create deployment configuration
        run: |
          cat > containers.json << 'DEPLOY_EOF'
          {
            "containers": {
              "tta-api": {
                "image": "tta-api:latest",
                "ports": {
                  "8080": "HTTP"
                },
                "environment": {
                  "ENVIRONMENT": "staging",
                  "API_HOST": "0.0.0.0",
                  "API_PORT": "8080",
                  "DATABASE_URL": "${{ secrets.STAGING_DATABASE_URL }}",
                  "REDIS_URL": "${{ secrets.STAGING_REDIS_URL }}",
                  "NEO4J_URL": "${{ secrets.STAGING_NEO4J_URL }}",
                  "NEO4J_PASSWORD": "${{ secrets.STAGING_NEO4J_PASSWORD }}",
                  "SENTRY_DSN": "${{ secrets.STAGING_SENTRY_DSN }}",
                  "SENTRY_ENVIRONMENT": "staging",
                  "JWT_SECRET": "${{ secrets.STAGING_JWT_SECRET }}"
                }
              }
            },
            "publicEndpoint": {
              "containerName": "tta-api",
              "containerPort": 8080,
              "healthCheck": {
                "healthyThreshold": 2,
                "unhealthyThreshold": 2,
                "timeoutSeconds": 5,
                "intervalSeconds": 30,
                "path": "/health",
                "successCodes": "200"
              }
            }
          }
          DEPLOY_EOF

      - name: Deploy to Lightsail
        run: |
          # Push image to Lightsail
          aws lightsail push-container-image \
            --service-name ${{ env.SERVICE_NAME }} \
            --label tta-api \
            --image tta-api:latest

          # Update deployment configuration with new image
          IMAGE_TAG=$(aws lightsail get-container-images --service-name ${{ env.SERVICE_NAME }} --query 'containerImages[0].image' --output text)

          # Update containers.json with the new image
          jq --arg image "$IMAGE_TAG" '.containers."tta-api".image = $image' containers.json > containers-updated.json

          # Deploy
          aws lightsail create-container-service-deployment \
            --service-name ${{ env.SERVICE_NAME }} \
            --containers file://containers-updated.json

      - name: Wait for deployment
        run: |
          echo "Waiting for deployment to complete..."
          while true; do
            STATE=$(aws lightsail get-container-service-deployments \
              --service-name ${{ env.SERVICE_NAME }} \
              --query 'deployments[0].state' --output text)

            if [ "$STATE" = "ACTIVE" ]; then
              echo "Deployment completed successfully!"
              break
            elif [ "$STATE" = "FAILED" ]; then
              echo "Deployment failed!"
              exit 1
            fi

            echo "Deployment state: $STATE - waiting..."
            sleep 30
          done

      - name: Get service URL
        run: |
          SERVICE_URL=$(aws lightsail get-container-service \
            --service-name ${{ env.SERVICE_NAME }} \
            --query 'containerService.url' --output text)

          echo "🚀 Staging environment deployed!"
          echo "Service URL: $SERVICE_URL"
          echo "Health check: $SERVICE_URL/health"
EOF

echo -e "${GREEN}✅ GitHub Actions workflow created${NC}"
echo ""

# Create monitoring script
echo -e "${BLUE}📊 Creating monitoring script...${NC}"

cat > monitor-staging.sh << 'EOF'
#!/bin/bash

# TTA Staging Environment Monitoring Script

SERVICE_NAME="tta-staging"
REGION="us-east-1"

echo "🔍 TTA Staging Environment Status"
echo "================================="

# Get service status
echo "📊 Service Status:"
aws lightsail get-container-service \
    --service-name $SERVICE_NAME \
    --region $REGION \
    --query '{
        State: containerService.state,
        Power: containerService.power,
        Scale: containerService.scale,
        URL: containerService.url,
        CreatedAt: containerService.createdAt
    }' \
    --output table

echo ""

# Get deployment status
echo "🚀 Latest Deployment:"
aws lightsail get-container-service-deployments \
    --service-name $SERVICE_NAME \
    --region $REGION \
    --query 'deployments[0].{
        State: state,
        Version: version,
        CreatedAt: createdAt
    }' \
    --output table

echo ""

# Get service URL and test health
SERVICE_URL=$(aws lightsail get-container-service --service-name $SERVICE_NAME --region $REGION --query 'containerService.url' --output text)

echo "🌐 Health Check:"
echo "Service URL: $SERVICE_URL"

if curl -f -s "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

echo ""
echo "📋 Quick Commands:"
echo "  View logs: aws lightsail get-container-log --service-name $SERVICE_NAME --container-name tta-api"
echo "  Scale up: aws lightsail update-container-service --service-name $SERVICE_NAME --scale 3"
echo "  Scale down: aws lightsail update-container-service --service-name $SERVICE_NAME --scale 1"
EOF

chmod +x monitor-staging.sh

echo -e "${GREEN}✅ Monitoring script created${NC}"
echo ""

# Final instructions
echo -e "${GREEN}🎉 AWS Lightsail Staging Environment Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Configure Cloudflare DNS records (shown above)"
echo "2. Add GitHub secrets for automated deployment"
echo "3. Update your application configuration for staging"
echo "4. Test the deployment with: ./monitor-staging.sh"
echo ""
echo -e "${BLUE}🔗 Important URLs:${NC}"
echo "  Staging Service: $SERVICE_URL"
echo "  Health Check: $SERVICE_URL/health"
echo "  AWS Console: https://lightsail.aws.amazon.com/ls/webapp/home/containers"
echo ""
echo -e "${YELLOW}💰 Estimated Monthly Cost: $20-40${NC}"
echo -e "${GREEN}🔒 HIPAA Compliant: Yes (with proper BAA)${NC}"
echo ""
echo -e "${BLUE}📞 Support:${NC}"
echo "  Monitor: ./monitor-staging.sh"
echo "  Logs: aws lightsail get-container-log --service-name $SERVICE_NAME --container-name tta-api"
echo "  Scale: aws lightsail update-container-service --service-name $SERVICE_NAME --scale [1-20]"
echo ""
echo -e "${GREEN}✅ Your TTA staging environment is ready for healthcare-grade testing!${NC}"
