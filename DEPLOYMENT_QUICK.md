# 🚀 AI Earth - Quick Deployment Guide

## **30-Second Setup (Local)**
```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```
Visit: `http://localhost:8787`

---

## **5-Minute Docker Setup**
```bash
docker build -t ai-earth .
docker run -d -p 8787:8787 -e AI_EARTH_ADMIN_TOKEN=secure-token ai-earth
```
Visit: `http://localhost:8787`

---

## **Production on Linux/VPS**

### 1. **Clone & Setup**
```bash
git clone https://github.com/mlandrew33-lang/Ai-earth-v1.8.1.git
cd Ai-earth-v1.8.1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your domain and admin token
nano .env
```

### 3. **Run with Gunicorn**
```bash
gunicorn --bind 0.0.0.0:8787 --workers 4 wsgi:app &
```

### 4. **Setup Nginx Reverse Proxy**
```bash
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl reload nginx
```

---

## **Environment Variables**

| Variable | Default | Purpose |
|----------|---------|---------|
| `AI_EARTH_PORT` | 8787 | Server port |
| `AI_EARTH_PUBLIC_URL` | - | Public domain for callbacks |
| `AI_EARTH_ADMIN_TOKEN` | Auto-generated | Admin authentication |
| `DEBUG` | False | Debug mode |

---

## **Health Check**
```bash
curl http://localhost:8787/health
```

Expected: `{"ok": true, "service": "ai-earth-economic-engine"}`

---

## **Admin Login**
1. Visit app dashboard
2. Click "Admin Login"
3. Enter token from `AI_EARTH_ADMIN_TOKEN`

---

## **Stop/Restart**
```bash
# Local
Ctrl+C

# Docker
docker stop ai-earth-engine

# Gunicorn
pkill -f gunicorn

# Systemd
sudo systemctl restart ai-earth
```

---

## **View Logs**
```bash
# Docker
docker logs ai-earth-engine -f

# Systemd
sudo journalctl -u ai-earth -f

# File
tail -f /var/log/ai-earth/error.log
```

---

## **Troubleshooting**

**Port already in use:**
```bash
lsof -i :8787
kill -9 <PID>
```

**Module not found:**
```bash
pip install -r requirements.txt
python -c "import web_app; print('✅ OK')"
```

**Admin token issues:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(24))"
# Set as AI_EARTH_ADMIN_TOKEN
```

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide.
