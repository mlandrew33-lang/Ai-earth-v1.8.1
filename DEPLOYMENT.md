# AI Earth Economic Engine - Deployment Guide

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env with your configuration

# Run development server
python app.py
```

Visit `http://localhost:8787` in your browser.

---

## Docker Deployment

### Development with Docker Compose

```bash
docker-compose up
```

### Production Deployment

```bash
# Build image
docker build -t ai-earth:latest .

# Run container
docker run -d \
  --name ai-earth \
  -p 8787:8787 \
  -e AI_EARTH_ADMIN_TOKEN=your-secure-token \
  -e AI_EARTH_PUBLIC_URL=https://your-domain.com \
  ai-earth:latest
```

---

## Production with Gunicorn + Nginx

### 1. Install Production Server

```bash
pip install -r requirements.txt
pip install gunicorn
```

### 2. Create Systemd Service

**File:** `/etc/systemd/system/ai-earth.service`

```ini
[Unit]
Description=AI Earth Economic Engine
After=network.target
Wants=network-online.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/app/ai-earth
Environment="PATH=/home/app/ai-earth/venv/bin"
Environment="AI_EARTH_ADMIN_TOKEN=your-secure-token"
Environment="AI_EARTH_PUBLIC_URL=https://your-domain.com"
ExecStart=/home/app/ai-earth/venv/bin/gunicorn \
    --bind 127.0.0.1:8787 \
    --workers 4 \
    --worker-class sync \
    --timeout 60 \
    --access-logfile /var/log/ai-earth/access.log \
    --error-logfile /var/log/ai-earth/error.log \
    wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-earth
sudo systemctl start ai-earth
sudo systemctl status ai-earth
```

### 4. Configure Nginx

Copy `nginx.conf` to `/etc/nginx/nginx.conf` and update domain:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Environment Configuration

### Development
```
AI_EARTH_PORT=8787
AI_EARTH_PUBLIC_URL=http://localhost:8787
DEBUG=True
LOG_LEVEL=DEBUG
```

### Production
```
AI_EARTH_PORT=8787
AI_EARTH_PUBLIC_URL=https://your-domain.com
AI_EARTH_ADMIN_TOKEN=<strong-random-token>
DEBUG=False
LOG_LEVEL=INFO
PAYMENT_MODE=live
```

---

## Security Checklist

- [ ] Set strong `AI_EARTH_ADMIN_TOKEN`
- [ ] Configure HTTPS/SSL certificates
- [ ] Enable firewall rules (allow 80, 443 only)
- [ ] Set `DEBUG=False` in production
- [ ] Configure payment provider credentials securely
- [ ] Regular backups of data
- [ ] Monitor logs for errors
- [ ] Keep dependencies updated

---

## Monitoring

### Health Check

```bash
curl http://localhost:8787/health
```

Expected response:
```json
{
  "ok": true,
  "service": "ai-earth-economic-engine",
  "external_execution_configured": false,
  "payment_mode": "sandbox",
  "live": 1
}
```

### Logs

```bash
# Systemd service logs
sudo journalctl -u ai-earth -f

# Application logs
tail -f /var/log/ai-earth/error.log
tail -f /var/log/ai-earth/access.log
```

---

## Scaling

### Load Balancing

For high traffic, use multiple Gunicorn workers:

```bash
gunicorn --workers 8 --worker-class sync wsgi:app
```

### Horizontal Scaling

1. Deploy multiple AI Earth instances
2. Use Nginx/HAProxy for load balancing
3. Share WORLD state via Redis or database
4. Implement session persistence

---

## Troubleshooting

### Application won't start
```bash
python app.py
# Check for import errors and missing dependencies
```

### Port already in use
```bash
lsof -i :8787
kill -9 <PID>
```

### Permission denied on logs
```bash
sudo mkdir -p /var/log/ai-earth
sudo chown www-data:www-data /var/log/ai-earth
sudo chmod 755 /var/log/ai-earth
```

### Admin login fails
```bash
# Generate new token
python -c "import secrets; print('Token:', secrets.token_urlsafe(24))"
# Set in AI_EARTH_ADMIN_TOKEN environment variable
```

---

## Performance Tips

1. **Workers**: Set to 2-4x number of CPU cores
2. **Timeout**: Increase for heavy simulations
3. **Caching**: Enable Nginx caching for `/api/dashboard`
4. **Compression**: Gzip enabled by default in nginx.conf
5. **Memory**: Monitor Gunicorn memory usage

---

## Backup & Restore

### Backup World State
```python
import json
from seed import seed_world

world = seed_world()
with open('backup.json', 'w') as f:
    json.dump(world.__dict__, f)
```

### Restore World State
```python
import json
from models import World

with open('backup.json', 'r') as f:
    data = json.load(f)
world = World(**data)
```

---

For questions or issues, check the [README.md](README.md) or create a GitHub issue.
