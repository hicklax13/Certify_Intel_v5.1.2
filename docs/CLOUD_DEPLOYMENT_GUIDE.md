# Certify Intel - Cloud Deployment Guide

Complete guide for deploying Certify Intel to AWS, Google Cloud Platform (GCP), and Microsoft Azure.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Deployment](#aws-deployment)
3. [Google Cloud Platform Deployment](#google-cloud-platform-deployment)
4. [Azure Deployment](#azure-deployment)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# Docker & Docker Compose
docker --version  # >= 20.10
docker-compose --version  # >= 2.0

# Cloud CLIs (install as needed)
aws --version       # AWS CLI v2
gcloud --version    # Google Cloud SDK
az --version        # Azure CLI
```

### Required Files

Ensure these files exist in your project:
- `docker-compose.prod.yml` - Production compose file
- `backend/Dockerfile.prod` - Production Dockerfile
- `backend/.env` - Environment configuration
- `nginx/nginx.conf` - Nginx configuration

### Environment Variables

Create `backend/.env` from `backend/.env.example`:

```env
# Required
SECRET_KEY=your-secure-random-key-here

# AI Configuration
OPENAI_API_KEY=sk-...
GOOGLE_AI_API_KEY=...

# Database (use cloud database URL for production)
DATABASE_URL=postgresql://user:pass@host:5432/certify_intel

# Optional
DESKTOP_MODE=false
```

---

## AWS Deployment

### Option A: AWS ECS (Elastic Container Service)

**Recommended for:** Production workloads with auto-scaling

#### Step 1: Create ECR Repository

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name certify-intel-backend --region us-east-1

# Build and push image
docker build -t certify-intel-backend -f backend/Dockerfile.prod backend/
docker tag certify-intel-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/certify-intel-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/certify-intel-backend:latest
```

#### Step 2: Create ECS Task Definition

Create `ecs-task-definition.json`:

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
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/certify-intel-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "PYTHONUNBUFFERED", "value": "1"}
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:certify-intel-secrets"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:certify-intel-secrets:OPENAI_API_KEY::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/certify-intel",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

#### Step 3: Create ECS Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name certify-intel-cluster

# Create service
aws ecs create-service \
  --cluster certify-intel-cluster \
  --service-name certify-intel-service \
  --task-definition certify-intel \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Step 4: Configure Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name certify-intel-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name certify-intel-targets \
  --protocol HTTP \
  --port 8000 \
  --target-type ip \
  --vpc-id vpc-xxx \
  --health-check-path /api/health
```

---

### Option B: AWS EC2 with Docker Compose

**Recommended for:** Simple deployments, development/staging

#### Step 1: Launch EC2 Instance

```bash
# Launch t3.medium instance with Amazon Linux 2
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxx \
  --subnet-id subnet-xxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=certify-intel}]'
```

#### Step 2: Install Docker on EC2

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

#### Step 3: Deploy Application

```bash
# SSH back in
ssh -i your-key.pem ec2-user@your-instance-ip

# Clone repository
git clone https://github.com/your-org/certify-intel.git
cd certify-intel

# Configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Edit with your values

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Verify
curl http://localhost/api/health
```

---

## Google Cloud Platform Deployment

### Option A: Google Cloud Run

**Recommended for:** Serverless, pay-per-use, auto-scaling

#### Step 1: Configure Project

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### Step 2: Build and Push Image

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build and push
docker build -t gcr.io/YOUR_PROJECT_ID/certify-intel-backend -f backend/Dockerfile.prod backend/
docker push gcr.io/YOUR_PROJECT_ID/certify-intel-backend
```

#### Step 3: Create Secrets

```bash
# Create secrets
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding SECRET_KEY \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### Step 4: Deploy to Cloud Run

```bash
gcloud run deploy certify-intel \
  --image gcr.io/YOUR_PROJECT_ID/certify-intel-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10 \
  --port 8000 \
  --set-secrets="SECRET_KEY=SECRET_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --set-env-vars="PYTHONUNBUFFERED=1,DATABASE_URL=sqlite:///./data/certify_intel.db"
```

---

### Option B: Google Kubernetes Engine (GKE)

**Recommended for:** Complex deployments, multi-service architectures

#### Step 1: Create GKE Cluster

```bash
gcloud container clusters create certify-intel-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials certify-intel-cluster --zone us-central1-a
```

#### Step 2: Create Kubernetes Manifests

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: certify-intel-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: certify-intel-backend
  template:
    metadata:
      labels:
        app: certify-intel-backend
    spec:
      containers:
      - name: backend
        image: gcr.io/YOUR_PROJECT_ID/certify-intel-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: certify-intel-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: certify-intel-service
spec:
  type: LoadBalancer
  selector:
    app: certify-intel-backend
  ports:
  - port: 80
    targetPort: 8000
```

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml
```

---

## Azure Deployment

### Option A: Azure Container Instances (ACI)

**Recommended for:** Simple deployments, quick setup

#### Step 1: Create Resource Group and Registry

```bash
# Login
az login

# Create resource group
az group create --name certify-intel-rg --location eastus

# Create container registry
az acr create --resource-group certify-intel-rg --name certifyintelacr --sku Basic

# Login to ACR
az acr login --name certifyintelacr
```

#### Step 2: Build and Push Image

```bash
# Build and push
docker build -t certifyintelacr.azurecr.io/certify-intel-backend -f backend/Dockerfile.prod backend/
docker push certifyintelacr.azurecr.io/certify-intel-backend
```

#### Step 3: Deploy Container Instance

```bash
# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --name certifyintelacr --query "passwords[0].value" -o tsv)

# Deploy container
az container create \
  --resource-group certify-intel-rg \
  --name certify-intel-container \
  --image certifyintelacr.azurecr.io/certify-intel-backend:latest \
  --cpu 1 \
  --memory 1 \
  --registry-login-server certifyintelacr.azurecr.io \
  --registry-username certifyintelacr \
  --registry-password $ACR_PASSWORD \
  --dns-name-label certify-intel \
  --ports 8000 \
  --environment-variables PYTHONUNBUFFERED=1 \
  --secure-environment-variables SECRET_KEY=your-secret-key OPENAI_API_KEY=sk-xxx
```

---

### Option B: Azure Kubernetes Service (AKS)

**Recommended for:** Production workloads, enterprise deployments

#### Step 1: Create AKS Cluster

```bash
# Create AKS cluster
az aks create \
  --resource-group certify-intel-rg \
  --name certify-intel-aks \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group certify-intel-rg --name certify-intel-aks

# Attach ACR to AKS
az aks update -n certify-intel-aks -g certify-intel-rg --attach-acr certifyintelacr
```

#### Step 2: Deploy with Helm or kubectl

Use the same Kubernetes manifests as GKE, replacing the image reference:

```yaml
image: certifyintelacr.azurecr.io/certify-intel-backend:latest
```

---

## Post-Deployment Configuration

### 1. Configure DNS

Point your domain to the cloud load balancer IP:

```bash
# AWS: Get ALB DNS
aws elbv2 describe-load-balancers --names certify-intel-alb --query 'LoadBalancers[0].DNSName'

# GCP: Get external IP
kubectl get service certify-intel-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Azure: Get FQDN
az container show --resource-group certify-intel-rg --name certify-intel-container --query ipAddress.fqdn
```

### 2. Configure SSL/TLS

**Using Let's Encrypt:**

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
```

### 3. Set Up Database Backup

**AWS RDS:**
```bash
# Enable automated backups
aws rds modify-db-instance \
  --db-instance-identifier certify-intel-db \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

**GCP Cloud SQL:**
```bash
gcloud sql instances patch certify-intel-db \
  --backup-start-time 03:00 \
  --enable-bin-log
```

---

## Monitoring & Maintenance

### Health Check Endpoints

| Endpoint | Expected Response | Purpose |
|----------|-------------------|---------|
| `/api/health` | `{"status": "healthy"}` | Basic health |
| `/api/competitors` | Array of competitors | Database connectivity |

### Log Access

**AWS CloudWatch:**
```bash
aws logs tail /ecs/certify-intel --follow
```

**GCP Cloud Logging:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=certify-intel"
```

**Azure Monitor:**
```bash
az monitor log-analytics query \
  --workspace certify-intel-workspace \
  --analytics-query "ContainerLog | where ContainerName == 'certify-intel'"
```

### Scaling

**AWS ECS:**
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/certify-intel-cluster/certify-intel-service \
  --min-capacity 1 \
  --max-capacity 10
```

**GCP Cloud Run:**
```bash
gcloud run services update certify-intel --max-instances 10
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Container won't start | Missing env vars | Check secrets are properly configured |
| Health check failing | Port mismatch | Verify container exposes port 8000 |
| Database connection error | Wrong DATABASE_URL | Update connection string |
| AI features not working | Missing API keys | Add OPENAI_API_KEY to secrets |
| Slow response times | Insufficient resources | Increase CPU/memory allocation |

### Debugging Commands

```bash
# Check container logs
docker logs certify_intel_api

# Check container status
docker ps -a

# Execute command in container
docker exec -it certify_intel_api /bin/bash

# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

---

## Cost Estimates

| Cloud | Service | Configuration | Est. Monthly Cost |
|-------|---------|---------------|-------------------|
| AWS | ECS Fargate | 2 tasks, 0.5 vCPU, 1GB | ~$30-50 |
| AWS | EC2 | t3.medium | ~$30 |
| GCP | Cloud Run | 1 vCPU, 1GB, min 1 instance | ~$20-40 |
| GCP | GKE | 2 e2-medium nodes | ~$50-70 |
| Azure | ACI | 1 vCPU, 1GB | ~$25-40 |
| Azure | AKS | 2 B2s nodes | ~$50-70 |

*Costs vary by region and usage patterns. Use cloud pricing calculators for accurate estimates.*

---

**Document Version:** 1.0
**Last Updated:** January 26, 2026
