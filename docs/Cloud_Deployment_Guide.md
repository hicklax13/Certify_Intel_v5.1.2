# Certify Intel - Cloud Deployment Guide

## Overview

This guide covers deploying Certify Intel to cloud platforms (AWS, Azure, or GCP).

---

## Option 1: AWS Deployment (Recommended)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Route 53  │──│     ALB     │──│    ECS Fargate      │  │
│  │   (DNS)     │  │  (HTTPS)    │  │  ├─ Backend API     │  │
│  └─────────────┘  └─────────────┘  │  ├─ Celery Worker   │  │
│                                     │  └─ Celery Beat     │  │
│                                     └─────────────────────┘  │
│                                               │               │
│  ┌─────────────┐  ┌─────────────┐  ┌────────┴────────────┐  │
│  │   S3        │  │  ElastiCache│  │    RDS PostgreSQL   │  │
│  │  (Static)   │  │   (Redis)   │  │    (Database)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Create RDS PostgreSQL Database

```bash
# Using AWS CLI
aws rds create-db-instance \
    --db-instance-identifier certify-intel-db \
    --db-instance-class db.t3.small \
    --engine postgres \
    --engine-version 15 \
    --master-username certify_admin \
    --master-user-password YOUR_SECURE_PASSWORD \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxx \
    --db-name certify_intel
```

### Step 2: Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id certify-intel-redis \
    --cache-node-type cache.t3.small \
    --engine redis \
    --num-cache-nodes 1
```

### Step 3: Create ECR Repository & Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name certify-intel-backend

# Build and push
docker build -t certify-intel-backend:latest -f docker/Dockerfile.backend .
docker tag certify-intel-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/certify-intel-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/certify-intel-backend:latest
```

### Step 4: Create ECS Task Definition

```json
{
  "family": "certify-intel",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/certify-intel-backend:latest",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://certify_admin:PASSWORD@RDS_ENDPOINT:5432/certify_intel"},
        {"name": "REDIS_URL", "value": "redis://ELASTICACHE_ENDPOINT:6379/0"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:certify-intel/openai"},
        {"name": "SMTP_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:certify-intel/smtp"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/certify-intel",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

### Step 5: Create Application Load Balancer with HTTPS

```bash
# Create ALB
aws elbv2 create-load-balancer \
    --name certify-intel-alb \
    --subnets subnet-xxx subnet-yyy \
    --security-groups sg-zzz

# Create target group
aws elbv2 create-target-group \
    --name certify-intel-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id vpc-xxx \
    --target-type ip \
    --health-check-path /health

# Create HTTPS listener (requires ACM certificate)
aws elbv2 create-listener \
    --load-balancer-arn ALB_ARN \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=ACM_CERT_ARN \
    --default-actions Type=forward,TargetGroupArn=TG_ARN
```

### Step 6: Create ECS Service

```bash
aws ecs create-service \
    --cluster certify-intel-cluster \
    --service-name certify-intel-backend \
    --task-definition certify-intel:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-zzz],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=TG_ARN,containerName=backend,containerPort=8000"
```

---

## Option 2: Azure Deployment

### Architecture

- **Azure Container Apps** - Backend and workers
- **Azure Database for PostgreSQL** - Database
- **Azure Cache for Redis** - Task queue
- **Azure Key Vault** - Secrets
- **Azure App Gateway** - HTTPS and WAF

### Quick Start with Azure CLI

```bash
# Create resource group
az group create --name certify-intel-rg --location eastus

# Create PostgreSQL
az postgres flexible-server create \
    --resource-group certify-intel-rg \
    --name certify-intel-db \
    --admin-user certify_admin \
    --admin-password YOUR_PASSWORD \
    --sku-name Standard_B1ms

# Create Redis
az redis create \
    --resource-group certify-intel-rg \
    --name certify-intel-redis \
    --sku Basic \
    --vm-size c0

# Create Container App
az containerapp create \
    --name certify-intel-backend \
    --resource-group certify-intel-rg \
    --environment certify-intel-env \
    --image YOUR_REGISTRY/certify-intel-backend:latest \
    --target-port 8000 \
    --ingress external \
    --env-vars DATABASE_URL=postgresql://... REDIS_URL=redis://...
```

---

## Option 3: Google Cloud (GCP) Deployment

### Architecture

- **Cloud Run** - Backend API (serverless)
- **Cloud SQL** - PostgreSQL database
- **Memorystore** - Redis cache
- **Cloud Scheduler** - Cron jobs
- **Secret Manager** - API keys

### Quick Deploy with gcloud

```bash
# Set project
gcloud config set project certify-intel

# Create Cloud SQL instance
gcloud sql instances create certify-intel-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create certify_intel --instance=certify-intel-db

# Deploy to Cloud Run
gcloud run deploy certify-intel-backend \
    --image gcr.io/certify-intel/backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL=... \
    --set-secrets OPENAI_API_KEY=openai-key:latest
```

---

## Environment Variables for Production

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/certify_intel
REDIS_URL=redis://host:6379/0
OPENAI_API_KEY=sk-...

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@yourdomain.com
SMTP_PASSWORD=app-password
ALERT_FROM_EMAIL=certify-intel@yourdomain.com
ALERT_TO_EMAILS=team@yourdomain.com

# Optional
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

---

## SSL/HTTPS Setup

### Option A: AWS Certificate Manager (Free)

```bash
aws acm request-certificate \
    --domain-name intel.certifyhealth.com \
    --validation-method DNS
```

### Option B: Let's Encrypt (Free)

```bash
# Using certbot
certbot certonly --standalone -d intel.certifyhealth.com
```

### Option C: Cloudflare (Recommended)

1. Add domain to Cloudflare
2. Update nameservers
3. Enable "Full (strict)" SSL mode
4. Proxy traffic through Cloudflare

---

## Domain Configuration

### Route 53 (AWS)

```bash
# Create hosted zone
aws route53 create-hosted-zone --name intel.certifyhealth.com

# Create A record pointing to ALB
aws route53 change-resource-record-sets \
    --hosted-zone-id ZONE_ID \
    --change-batch '{"Changes":[{"Action":"CREATE","ResourceRecordSet":{"Name":"intel.certifyhealth.com","Type":"A","AliasTarget":{"DNSName":"ALB_DNS","HostedZoneId":"ALB_ZONE","EvaluateTargetHealth":true}}}]}'
```

---

## Cost Estimates

| Component | AWS (Monthly) | Azure (Monthly) | GCP (Monthly) |
|-----------|---------------|-----------------|---------------|
| Compute | $30-50 | $30-50 | $20-40 |
| Database | $15-25 | $15-25 | $10-20 |
| Redis | $15 | $15 | $15 |
| Storage | $5 | $5 | $5 |
| **Total** | **$65-95** | **$65-95** | **$50-80** |

---

## Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Environment variables set
- [ ] SSL certificate active
- [ ] Health check passing
- [ ] Celery workers running
- [ ] Email alerts tested
- [ ] Domain DNS configured
- [ ] Monitoring enabled
- [ ] Backup configured
