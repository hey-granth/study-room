#!/bin/bash
# scripts/ec2-setup.sh
# Run ONCE on a fresh Ubuntu 24.04 t3.micro instance to install all dependencies.
# Usage: bash ec2-setup.sh
#
# After this script completes, follow the printed "Next steps" to finish deployment.
set -euo pipefail

DOMAIN="studyapi.granth.tech"
APP_DIR="/home/ubuntu/studyroom"

echo "=== [1/6] Updating system packages ==="
sudo apt-get update && sudo apt-get upgrade -y

echo "=== [2/6] Installing Docker ==="
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker ubuntu
# You must log out and back in (or run 'newgrp docker') for group to take effect.

echo "=== [3/6] Installing Docker Compose plugin ==="
sudo apt-get install -y docker-compose-plugin

echo "=== [4/6] Installing Nginx, Certbot, and AWS CLI ==="
sudo apt-get install -y nginx certbot python3-certbot-nginx awscli

echo "=== [5/6] Configuring Docker log rotation ==="
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
sudo systemctl restart docker

echo "=== [6/6] Creating application directory ==="
mkdir -p "$APP_DIR"
sudo chown ubuntu:ubuntu "$APP_DIR"

echo ""
echo "✅ EC2 base setup complete."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps (run in order):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Point your DNS: $DOMAIN → this EC2 Elastic IP."
echo "     Wait for propagation (check with: dig $DOMAIN)"
echo ""
echo "  2. Copy files to EC2:"
echo "     scp -i your-key.pem backend/docker-compose.yml ubuntu@<EC2_IP>:$APP_DIR/"
echo "     scp -i your-key.pem backend/nginx/studyroom.conf ubuntu@<EC2_IP>:/tmp/"
echo "     scp -i your-key.pem backend/.env.example ubuntu@<EC2_IP>:$APP_DIR/.env"
echo ""
echo "  3. Fill in your .env on EC2:"
echo "     nano $APP_DIR/.env"
echo "     (Set DATABASE_URL from Neon, REDIS_URL from Upstash, JWT_SECRET_KEY, etc.)"
echo ""
echo "  4. Install Nginx config:"
echo "     sudo cp /tmp/studyroom.conf /etc/nginx/sites-available/studyroom"
echo "     sudo ln -s /etc/nginx/sites-available/studyroom /etc/nginx/sites-enabled/"
echo "     sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "  5. Obtain SSL certificate:"
echo "     sudo certbot --nginx -d $DOMAIN"
echo "     sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "  6. Pull and start the API container:"
echo "     cd $APP_DIR"
echo "     # Authenticate with ECR (requires AWS IAM role on the instance):"
echo "     aws ecr get-login-password --region us-east-1 | \\"
echo "       docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com"
echo "     docker compose up -d"
echo ""
echo "  7. Run Alembic migrations against Neon:"
echo "     docker compose exec api alembic upgrade head"
echo ""
echo "  8. Verify everything works:"
echo "     curl https://$DOMAIN/health"
echo ""
