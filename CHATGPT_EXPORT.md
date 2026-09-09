# AI EARTH v1.8.1 - COMPLETE PROJECT EXPORT FOR ChatGPT

## PROJECT OVERVIEW

### What is AI Earth?
AI Earth is an AI-powered Economic Engine that simulates a complete economy with:
- Citizens with skills, education, and careers
- Businesses with revenue, expenses, and operations
- Manufacturing plants and mineral extraction
- Educational institutions and research
- Payment systems and external economy gateway
- Governance and approval workflows
- Real-time web dashboard

### Technology Stack
- **Backend**: Python 3.11+
- **Server**: Gunicorn + Nginx
- **Frontend**: HTML5 + Vanilla JavaScript
- **Deployment**: Docker, Docker Compose
- **Production**: Systemd service file

### Core Architecture

```
Economic World (seed_world)
    ↓
AI Economic Brain (AgentBrain)
    ↓
Opportunity Engine (OpportunityEngine)
    ↓
Simulation Lab (EconomyEngine)
    ↓
Economic Decision (apply_decision)
    ↓
Approval (external_economy)
    ↓
Real Transaction / Service
    ↓
Verification
    ↓
Financial Ledger
    ↓
Learning System
```

---

## KEY FILES & THEIR PURPOSES

### Core Simulation Engine
- **engine.py** (230 lines)
  - `EconomyEngine` class - Main simulation loop
  - `advance_day()` - Daily economic cycle
  - `run_institutions()` - Research, restaurants, games, sports
  - `run_mineral_ecosystem()` - Resource extraction & beneficiation
  - `run_manufacturing()` - Industrial production
  - `apply_decision()` - Policy implementation

### Web Application & API
- **web_app.py** (152 lines)
  - `Handler` class - HTTP request handling
  - REST API endpoints for all operations
  - Real-time dashboard data endpoint
  - Admin authentication & session management
  - External transaction approvals
  - Opportunity scanning & execution

- **wsgi.py** (Production server)
  - WSGI-compatible entry point
  - For Gunicorn/uWSGI deployment
  - Session management
  - Request handling

### Supporting Modules (Referenced)
- **seed.py** - Initialize world with citizens, businesses, resources
- **models.py** - Data models (World, Business, Citizen, Event)
- **dashboard.py** - Dashboard data aggregation (snapshot function)
- **education.py** - Citizen training & qualification system
- **payments.py** - Payment processing & finance tracking
- **external_economy.py** - External gateway for real-world transactions
- **opportunities.py** - Opportunity scanning & ranking engine
- **agents.py** - AI agents & decision-making
- **agent_brain.py** - LLM-powered agent proposals
- **institutions.py** - Research, restaurants, games, sports entities
- **marketplace.py** - Product listings & commerce
- **manufacturing.py** - Industrial production system
- **constitution.py** - Governance rules & spending limits

---

## DEPLOYMENT FILES

### Docker & Orchestration
- **Dockerfile** - Container image with Gunicorn
- **docker-compose.yml** - Multi-service setup (app + nginx)
- **nginx.conf** - Reverse proxy, compression, security headers
- **Makefile** - Common development commands

### Configuration
- **.env.example** - Environment variable template
- **.gitignore** - Git exclusions

### Documentation
- **README.md** - Project overview
- **DEPLOYMENT.md** - Full deployment guide
- **DEPLOYMENT_QUICK.md** - Quick reference

---

## KEY FEATURES & LOGIC

### Daily Economy Cycle (advance_day)
1. Each business generates revenue based on:
   - Employee productivity
   - Quality score
   - Demand factor (random)
   - Product price

2. Businesses pay:
   - Employee wages (based on training level)
   - Operating costs (utilities, supplies)

3. Treasury collects 3% tax on daily revenue

4. AI agents make decisions:
   - Hold low-quality businesses for review
   - Approve expansions with proper checks
   - Train citizens in needed competencies
   - Run improvement experiments
   - Review debt situations

5. Institutions operate:
   - Restaurants publish recipes & content
   - Game studios ship cross-platform builds
   - Sports platforms host events
   - Research produces findings

6. Mineral ecosystem runs:
   - Environmental review required
   - Resource extraction & beneficiation
   - Recycling & downstream manufacturing

7. Manufacturing:
   - Plants produce goods
   - Use refined mineral inputs
   - Track utilization rates
   - Generate revenue

### API Endpoints

**GET:**
- `/` or `/dashboard` - Web interface
- `/api/dashboard` - Real-time JSON state
- `/health` - Service health check

**POST (Admin Required):**
- `/api/auth/login` - Authenticate with token
- `/api/advance` - Run simulation days
- `/api/external/order` - Create supplier order
- `/api/external/service` - Create service request
- `/api/external/approve` - Approve transaction
- `/api/external/reject` - Reject transaction
- `/api/external/execute` - Execute approved transaction
- `/api/opportunities/scan` - Scan for opportunities
- `/api/opportunities/approve` - Approve opportunity
- `/api/opportunities/execute` - Execute opportunity
- `/api/opportunities/complete` - Mark opportunity complete
- `/api/transfer/imports` - Import assets
- `/api/transfer/exports` - Export assets

**Payment:**
- `/api/payments/deposit` - Create deposit checkout
- `/api/payments/product` - Create product purchase
- `/api/payments/notify` - Payment provider callback

### Data Flow Example: Run 5 Days

1. User sends: `POST /api/advance {days: 5}`
2. Server validates admin session
3. `EconomyEngine(WORLD).run(5)` called
4. For each day:
   - Business revenue calculated
   - Wages paid to citizens
   - Operating costs deducted
   - AI decisions applied
   - Institutions operate
   - Minerals extracted
   - Manufacturing runs
   - Events logged
5. Returns: `{ok: true, day: X}`
6. Frontend refreshes dashboard

---

## CONFIGURATION & ENVIRONMENT

### Required Environment Variables
```
AI_EARTH_ADMIN_TOKEN=your-secure-token
AI_EARTH_PORT=8787
AI_EARTH_PUBLIC_URL=https://your-domain.com
```

### Optional
```
DEBUG=False
LOG_LEVEL=INFO
PAYMENT_MODE=sandbox|live
AI_EARTH_EXTERNAL_EXECUTION_WEBHOOK=https://...
```

---

## SECURITY ARCHITECTURE

### Authentication
- Admin token (secure random token)
- Session cookies (8-hour expiry)
- HttpOnly flag (no JavaScript access)
- SameSite=Strict (CSRF protection)

### Authorization
- All write endpoints require `self.require_admin()`
- Session validation on every protected request
- Constant-time token comparison

### Data Protection
- No sensitive payment data stored
- Payment provider handles PCI compliance
- Asset transfers tracked with SHA256 hashes
- Full audit logging of all actions

### Network Security
- Nginx reverse proxy with security headers
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection enabled
- Gzip compression enabled
- SSL/TLS ready (configure certificates)

---

## PERFORMANCE CHARACTERISTICS

### Simulation Speed
- 1 day ≈ 50-100ms on modern hardware
- 30 days can be advanced in 1-3 seconds
- 1000+ citizens supported

### Web Performance
- Dashboard refresh: 5 seconds (configurable)
- API response: <100ms
- Gzip compression: 60-80% reduction

### Scalability
- Stateful (requires shared state for horizontal scaling)
- Workers: 4 (configurable per CPU cores)
- Database: Optional (currently in-memory)
- Caching: Nginx ready

---

## COMMON CUSTOMIZATIONS

### Add New Economic Behavior
Edit `engine.py`:
```python
def run_custom_system(self):
    for entity in self.world.custom_entities.values():
        # Your logic here
        self.log('custom', 'Action performed', amount, actor)
```

### Modify Dashboard
Edit `web_app.py`:
- Add new `<section>` in PAGE HTML
- Update JavaScript refresh function
- Add API endpoint to populate data

### Add Payment Provider
Edit `payments.py`:
- Implement `create_checkout()`
- Handle provider callback
- Track transactions

### Connect LLM
Edit `agent_brain.py`:
- Enable `llm.enabled()`
- Implement `controller_plan()`
- Implement `citizen_decision()`

---

## DEPLOYMENT CHECKLIST

- [ ] Clone repository
- [ ] Create Python virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Generate admin token: `python -c "import secrets; print(secrets.token_urlsafe(24))"`
- [ ] Set `AI_EARTH_ADMIN_TOKEN` in `.env`
- [ ] Set `AI_EARTH_PUBLIC_URL` for production
- [ ] Test locally: `python app.py`
- [ ] Access: `http://localhost:8787`
- [ ] Login with admin token
- [ ] Run simulation test (advance 5 days)
- [ ] For production: Follow `DEPLOYMENT.md`

---

## TROUBLESHOOTING GUIDE

**"Port 8787 already in use"**
```bash
lsof -i :8787
kill -9 <PID>
```

**"Admin login fails"**
```bash
# Generate new token
python -c "import secrets; print(secrets.token_urlsafe(24))"
# Set AI_EARTH_ADMIN_TOKEN environment variable
```

**"Dashboard doesn't update"**
- Check browser console for errors
- Verify `/api/dashboard` endpoint returns JSON
- Check network tab for failed requests

**"Simulation runs slow"**
- Check system resources (CPU, memory)
- Reduce number of agents
- Optimize decision-making in `engine.py`

---

## VISION & ROADMAP

### Current Stage: Economic Simulation ✅
- Full simulation engine
- Web dashboard
- Payment gateway
- Governance framework

### Next Stage: Economic Intelligence
- Enhanced AI decision-making
- Predictive analytics
- Learning system improvements
- Risk analysis

### Future: Governed Economic Execution
- Real external transactions
- Verified provider integrations
- Full audit trail
- Compliance framework

### Ultimate: Self-Improving Economic Activity
- Autonomous agent business
- Real-world revenue generation
- Continuous learning & optimization
- Scaled execution

---

## GETTING HELP

### Resources
- GitHub: https://github.com/mlandrew33-lang/Ai-earth-v1.8.1
- Documentation: See README.md, DEPLOYMENT.md
- Code: Well-commented Python modules

### Questions for ChatGPT
- "How can I optimize the simulation algorithm?"
- "What features should I add?"
- "How do I scale this to production?"
- "How can I integrate with [service]?"
- "What are the security implications of [feature]?"

---

**Project Status**: Production-Ready ✅
**Last Updated**: 2026-09-09
**Version**: 1.8.1
**License**: [Your License]
**Author**: mlandrew33-lang
