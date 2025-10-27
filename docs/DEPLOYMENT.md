# Deployment Guide - Claude Vision & Hands

**Version**: 2.0.0
**Last Updated**: 2025-10-27
**Status**: Production-Ready

---

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Bare Metal Deployment](#bare-metal-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Configuration](#configuration)
7. [Monitoring](#monitoring)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Deployment Options

### Option 1: Docker Compose (Recommended)
- **Best for**: Development, small-scale production
- **Difficulty**: Easy
- **Time**: 10 minutes
- **Scalability**: Single server

### Option 2: Kubernetes
- **Best for**: Large-scale production, high availability
- **Difficulty**: Advanced
- **Time**: 1-2 hours
- **Scalability**: Horizontal scaling

### Option 3: Bare Metal
- **Best for**: Maximum performance, full control
- **Difficulty**: Medium
- **Time**: 30 minutes
- **Scalability**: Manual

### Option 4: Cloud (AWS/GCP/Azure)
- **Best for**: Managed infrastructure, auto-scaling
- **Difficulty**: Medium
- **Time**: 1 hour
- **Scalability**: Cloud-native

---

## Docker Deployment

### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### Quick Start

**1. Clone Repository**:
```bash
cd ~
git clone https://github.com/your-username/claude-vision-hands.git
cd claude-vision-hands
```

**2. Configure Environment**:
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Configuration**:
```bash
# Add your Gemini API key
GEMINI_API_KEY=your-api-key-here

# Set production mode
CLAUDE_VISION_MODE=production

# Configure security
SECURITY_STRICT_MODE=true
```

**3. Build and Start**:
```bash
# Build containers
docker compose build

# Start services
docker compose up -d

# Check status
docker compose ps
```

**4. Verify Deployment**:
```bash
# Check logs
docker compose logs -f claude-vision-hands

# Test health endpoint
curl http://localhost:8080/health

# Access API
curl http://localhost:8081/api/status
```

### Docker Compose Configuration

**Full Stack with Monitoring**:
```bash
# Start with monitoring
docker compose --profile monitoring up -d

# Services started:
# - claude-vision-hands (main application)
# - chromadb (vector database)
# - redis (cache)
# - prometheus (metrics)
# - grafana (dashboards)
```

**Production Configuration**:
```bash
# Use production compose file
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Container Management

**View Logs**:
```bash
# All services
docker compose logs

# Specific service
docker compose logs claude-vision-hands

# Follow logs
docker compose logs -f --tail=100 claude-vision-hands
```

**Restart Services**:
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart claude-vision-hands
```

**Update Application**:
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build
```

**Stop Services**:
```bash
# Stop all services
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove volumes (CAUTION: deletes data)
docker compose down -v
```

### Resource Limits

**Configure Resource Limits** (docker-compose.yml):
```yaml
services:
  claude-vision-hands:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

### Kubernetes Manifests

**1. Namespace**:
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: claude-vision-hands
```

**2. ConfigMap**:
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: claude-config
  namespace: claude-vision-hands
data:
  CLAUDE_VISION_MODE: "production"
  LOG_LEVEL: "INFO"
  CHROMA_HOST: "chromadb-service"
  REDIS_HOST: "redis-service"
```

**3. Secret**:
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: claude-secrets
  namespace: claude-vision-hands
type: Opaque
data:
  GEMINI_API_KEY: <base64-encoded-key>
  REDIS_PASSWORD: <base64-encoded-password>
```

**Create secret**:
```bash
kubectl create secret generic claude-secrets \
  --from-literal=GEMINI_API_KEY=your-api-key \
  --from-literal=REDIS_PASSWORD=your-redis-password \
  -n claude-vision-hands
```

**4. Deployment**:
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claude-vision-hands
  namespace: claude-vision-hands
spec:
  replicas: 3
  selector:
    matchLabels:
      app: claude-vision-hands
  template:
    metadata:
      labels:
        app: claude-vision-hands
    spec:
      containers:
      - name: claude-vision-hands
        image: your-registry/claude-vision-hands:latest
        ports:
        - containerPort: 8080
          name: mcp
        - containerPort: 8081
          name: api
        envFrom:
        - configMapRef:
            name: claude-config
        - secretRef:
            name: claude-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: claude-data-pvc
```

**5. Service**:
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: claude-vision-hands
  namespace: claude-vision-hands
spec:
  selector:
    app: claude-vision-hands
  ports:
  - name: mcp
    port: 8080
    targetPort: 8080
  - name: api
    port: 8081
    targetPort: 8081
  type: LoadBalancer
```

**6. Persistent Volume Claim**:
```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: claude-data-pvc
  namespace: claude-vision-hands
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n claude-vision-hands

# Check service
kubectl get svc -n claude-vision-hands

# View logs
kubectl logs -f deployment/claude-vision-hands -n claude-vision-hands
```

### Horizontal Pod Autoscaling

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: claude-hpa
  namespace: claude-vision-hands
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: claude-vision-hands
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Bare Metal Deployment

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- OS: Ubuntu 20.04+ / Debian 11+

**Recommended**:
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB SSD
- OS: Ubuntu 22.04 LTS

### Installation

**1. System Preparation**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    build-essential

# Create user
sudo useradd -r -s /bin/bash -d /opt/claude claude
sudo mkdir -p /opt/claude
sudo chown claude:claude /opt/claude
```

**2. Application Setup**:
```bash
# Switch to claude user
sudo -u claude -i

# Clone repository
cd /opt/claude
git clone https://github.com/your-username/claude-vision-hands.git
cd claude-vision-hands

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**3. Configuration**:
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Set API key
export GEMINI_API_KEY="your-api-key"
```

**4. Database Setup**:
```bash
# Install ChromaDB dependencies
sudo apt install -y sqlite3

# Create data directories
mkdir -p ~/.claude-vision-hands/{memory,recordings,logs}
```

**5. Install System Service**:
```bash
# Create systemd service
sudo nano /etc/systemd/system/claude-vision-hands.service
```

```ini
[Unit]
Description=Claude Vision & Hands Autonomous AI System
After=network.target

[Service]
Type=simple
User=claude
Group=claude
WorkingDirectory=/opt/claude/claude-vision-hands
Environment="PATH=/opt/claude/claude-vision-hands/venv/bin"
Environment="GEMINI_API_KEY=your-api-key"
ExecStart=/opt/claude/claude-vision-hands/venv/bin/python3 -m integration.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**6. Start Service**:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable claude-vision-hands

# Start service
sudo systemctl start claude-vision-hands

# Check status
sudo systemctl status claude-vision-hands
```

**7. Setup Nginx Reverse Proxy** (Optional):
```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/claude-vision-hands
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /mcp {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/claude-vision-hands /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**8. Setup SSL with Let's Encrypt**:
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Cloud Deployment

### AWS Deployment

**Using EC2**:

**1. Launch EC2 Instance**:
```bash
# Instance type: t3.medium or larger
# AMI: Ubuntu 22.04 LTS
# Storage: 30 GB gp3
# Security Group: Allow ports 22, 80, 443, 8080, 8081
```

**2. Connect and Setup**:
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow bare metal installation steps
```

**Using ECS (Elastic Container Service)**:

**1. Create ECR Repository**:
```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name claude-vision-hands

# Build and push image
docker build -t claude-vision-hands .
docker tag claude-vision-hands:latest your-account.dkr.ecr.us-east-1.amazonaws.com/claude-vision-hands:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/claude-vision-hands:latest
```

**2. Create ECS Cluster**:
```bash
# Create cluster
aws ecs create-cluster --cluster-name claude-cluster

# Create task definition (task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster claude-cluster \
  --service-name claude-service \
  --task-definition claude-vision-hands \
  --desired-count 2 \
  --launch-type FARGATE
```

### Google Cloud Platform

**Using Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/claude-vision-hands
gcloud run deploy claude-vision-hands \
  --image gcr.io/your-project/claude-vision-hands \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key
```

### Azure Deployment

**Using Container Instances**:
```bash
# Create resource group
az group create --name claude-rg --location eastus

# Deploy container
az container create \
  --resource-group claude-rg \
  --name claude-vision-hands \
  --image your-registry/claude-vision-hands:latest \
  --cpu 2 --memory 4 \
  --ports 8080 8081 \
  --environment-variables GEMINI_API_KEY=your-key
```

---

## Configuration

### Environment Variables

See `.env.example` for full list of configuration options.

**Critical Settings**:
```bash
# API Keys
GEMINI_API_KEY=required

# Mode
CLAUDE_VISION_MODE=production

# Security
SECURITY_STRICT_MODE=true
```

### Configuration Files

**Master Configuration**: `config/master_config.yaml`

**Security Configuration**: `config/security_config.yaml`

**Memory Configuration**: `config/memory_config.yaml`

---

## Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8080/health

# Database health
curl http://localhost:8000/api/v1/heartbeat

# Redis health
redis-cli ping
```

### Prometheus Metrics

Access at: `http://localhost:9090`

**Key Metrics**:
- Request rate
- Error rate
- Response time
- Memory usage
- CPU usage

### Grafana Dashboards

Access at: `http://localhost:3000`

**Default credentials**: admin/admin

**Available Dashboards**:
- System Overview
- Security Events
- Memory System
- Workflow Performance

---

## Backup & Recovery

### Backup Strategy

**What to Backup**:
1. ChromaDB database (`/data/memory`)
2. Workflow recordings (`/data/recordings`)
3. Configuration files (`config/`)
4. Audit logs (`/data/logs`)

**Backup Script**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/claude-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup data
cp -r /data/memory "$BACKUP_DIR/"
cp -r /data/recordings "$BACKUP_DIR/"
cp -r /data/logs "$BACKUP_DIR/"
cp -r config/ "$BACKUP_DIR/"

# Compress
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR.tar.gz" s3://your-bucket/backups/
```

**Automate Backups**:
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/claude/backup.sh
```

### Recovery

**Restore from Backup**:
```bash
# Extract backup
tar -xzf backup-20251027-020000.tar.gz

# Stop services
docker compose down

# Restore data
cp -r backup-20251027-020000/memory /data/
cp -r backup-20251027-020000/recordings /data/
cp -r backup-20251027-020000/config ./

# Start services
docker compose up -d
```

---

## Troubleshooting

### Common Issues

**1. Container Won't Start**:
```bash
# Check logs
docker compose logs claude-vision-hands

# Check configuration
docker compose config

# Verify environment
docker compose exec claude-vision-hands env
```

**2. Database Connection Failed**:
```bash
# Check ChromaDB
docker compose logs chromadb

# Test connection
docker compose exec claude-vision-hands python3 -c "
import chromadb
client = chromadb.HttpClient(host='chromadb', port=8000)
print(client.heartbeat())
"
```

**3. High Memory Usage**:
```bash
# Check memory stats
docker stats

# Restart with limits
docker compose down
docker compose up -d
```

**4. Performance Issues**:
```bash
# Enable profiling
export PROFILING_ENABLED=true

# Check slow queries
grep "slow query" /data/logs/audit.log

# Optimize ChromaDB
docker compose exec chromadb chroma optimize
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall
- [ ] Enable audit logging
- [ ] Set up backups
- [ ] Configure monitoring
- [ ] Review security settings
- [ ] Update dependencies
- [ ] Rotate API keys
- [ ] Enable rate limiting

---

## Support

**Documentation**: https://docs.your-domain.com

**Issues**: https://github.com/your-username/claude-vision-hands/issues

**Community**: https://community.your-domain.com

---

**Production deployment is now complete! Monitor your system and enjoy autonomous AI automation.**

**Version**: 2.0.0
**Last Updated**: 2025-10-27
**Status**: ✅ Production-Ready
