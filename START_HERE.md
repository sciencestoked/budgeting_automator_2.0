# Budget Automation 2.0 - Start Here! 🚀

**Welcome back!** This document tells you exactly where to begin.

---

## ✅ What's Already Done

**Phase 1: Backend (COMPLETE)**
- FastAPI server with SQLite database
- Transaction storage + auto-categorization
- Duplicate detection
- Data collection endpoints for analysis
- All code committed to Git

---

## 🎯 Your Next Steps (In Order)

### Step 1: Set Up Tailscale (15 minutes) ✅ DONE
**Why:** Secure SSH access to your Ubuntu server from anywhere (no port forwarding!)

**Follow:** [QUICKSTART.md](QUICKSTART.md#2-set-up-tailscale-for-remote-ssh-access-) - Section 2

**What you'll get:**
```bash
ssh homeserver  # Works from anywhere!
```

---

### Step 2: Deploy to Ubuntu Server (30 minutes)
**Follow:** [QUICKSTART.md](QUICKSTART.md#3-deploy-backend-to-ubuntu-server) - Section 3

**Commands:**
```bash
# Clone repo ✅ DONE
git clone https://github.com/yourusername/budgeting_automator_2.0.git

# Install dependencies
cd budgeting_automator_2.0/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up systemd service (auto-start on boot)
sudo nano /etc/systemd/system/budget-api.service
# (Copy config from QUICKSTART.md)
sudo systemctl enable budget-api
sudo systemctl start budget-api
```

---

### Step 3: Set Up Cloudflare Tunnel (20 minutes)
**Why:** iPhone can send transactions to your server via HTTPS

**Follow:** [QUICKSTART.md](QUICKSTART.md#4-set-up-cloudflare-tunnel-for-iphone-access) - Section 4

**What you'll get:**
- Public URL: `https://budget.yourdomain.com/api/webhook`
- Your iPhone sends transaction data here
- Zero router configuration needed

---

### Step 4: Clean Up Old Setup (10 minutes)
**If you had old port forwarding:**

**Follow:** [QUICKSTART.md](QUICKSTART.md#5-clean-up-old-port-forwarding-important) - Section 5

**This will:**
- Remove port forwarding from router
- Stop No-IP service
- Fix router stability issues
- Prevent IP blacklisting

---

### Step 5: Set Up Remote Development (Optional, 10 minutes)
**Why:** Code directly on your server using VS Code

**Follow:** [REMOTE_DEVELOPMENT.md](REMOTE_DEVELOPMENT.md)

**Recommended method:** VS Code Remote SSH
- Full IDE on remote server
- No file syncing needed
- Integrated terminal
- Live debugging

---

### Step 6: Create Data Collection Shortcut (20 minutes)
**Goal:** Collect raw transaction data for 1 week to analyze patterns

**Follow:** [QUICKSTART.md](QUICKSTART.md#phase-2-data-collection-strategy) - Phase 2

**Steps:**
1. Create "Budget Data Dump" shortcut on iPhone
2. For 1 week: copy transaction emails/notifications and run shortcut
3. After 1 week: analyze what data you got
4. Build smart parsers based on patterns

**Detailed guide:** [shortcuts/DATA_EXTRACTION_GUIDE.md](shortcuts/DATA_EXTRACTION_GUIDE.md)

---

## 📚 Full Documentation Index

**Start Here:**
1. **[QUICKSTART.md](QUICKSTART.md)** ⭐ - Complete deployment guide
2. **[REMOTE_DEVELOPMENT.md](REMOTE_DEVELOPMENT.md)** 🖥️ - VS Code remote setup

**In-Depth:**
- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Full 9-phase roadmap
- [shortcuts/DATA_EXTRACTION_GUIDE.md](shortcuts/DATA_EXTRACTION_GUIDE.md) - iOS automation deep dive

**Reference:**
- [README.md](README.md) - Project overview
- API docs: `http://localhost:8000/docs` (when server running)

---

## 🔥 Quick Commands

### Start Local Development
```bash
cd /Users/s-singhal/budgeting_automator_2.0/backend
source venv/bin/activate
python -m app.main
# Open: http://localhost:8000/docs
```

### SSH to Server
```bash
ssh homeserver
```

### Deploy Code to Server
```bash
# After making changes on Mac:
git push

# Then on server:
ssh homeserver
cd budgeting_automator_2.0
git pull
sudo systemctl restart budget-api
sudo systemctl status budget-api
```

### Check Server Logs
```bash
ssh homeserver
journalctl -u budget-api -f
```

### Test API
```bash
# Test webhook:
curl -X POST https://budget.yourdomain.com/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "timestamp": "2025-10-27T12:00:00+09:00",
    "vendor": "Test Store",
    "amount": 1000,
    "currency": "JPY",
    "payment_method": "credit_card"
  }'

# Check transactions:
curl https://budget.yourdomain.com/api/transactions | python3 -m json.tool
```

---

## 🎓 Learning Path

**Week 1: Setup**
- ✅ Install Tailscale
- ✅ Deploy backend to server
- ✅ Set up Cloudflare Tunnel
- ✅ Test API

**Week 2: Data Collection**
- ✅ Create data dump shortcut
- ✅ Collect raw transaction data (emails, notifications)
- ✅ Analyze patterns

**Week 3: Smart Parsing**
- Build regex parsers for each source
- Implement vendor normalization
- Add smart duplicate detection

**Week 4: Email Reports**
- Set up daily/weekly/monthly summaries
- Configure APScheduler
- Test email delivery

**Month 2: Web Dashboard**
- Build React frontend
- Add charts and visualizations
- Implement goals/alerts UI

---

## 🆘 Troubleshooting

### Can't SSH to server
```bash
# Test Tailscale:
tailscale ping your-server-name

# If that fails, restart Tailscale:
sudo tailscale down
sudo tailscale up
```

### API not responding
```bash
# Check if running:
ssh homeserver
sudo systemctl status budget-api

# View logs:
journalctl -u budget-api -n 50

# Restart:
sudo systemctl restart budget-api
```

### Cloudflare Tunnel not working
```bash
# Check tunnel status:
ssh homeserver
sudo systemctl status cloudflared

# Test manually:
cloudflared tunnel run budget-automation

# View logs:
journalctl -u cloudflared -f
```

### Router still crashing
**Make sure you:**
1. Removed ALL port forwarding rules from router
2. Stopped No-IP service on server
3. Rebooted router after removing rules

---

## 💡 Pro Tips

**Development:**
- Use VS Code Remote SSH for best experience
- Keep tmux session running for long tasks
- Commit frequently to Git

**Security:**
- Never commit `.env` file
- Keep Tailscale running on server (auto-starts)
- Use strong password or SSH keys

**Deployment:**
- Test changes locally first
- Use git for all code changes
- Check logs after deploying

**Monitoring:**
- Check `systemctl status budget-api` daily
- Watch `journalctl -f` during development
- Set up email alerts for errors (Phase 4)

---

## 🎯 Current Project Status

**Completed:**
- ✅ Backend API (FastAPI + SQLite)
- ✅ Database models
- ✅ Auto-categorization
- ✅ Duplicate detection
- ✅ Data collection system
- ✅ Documentation (all guides)

**In Progress:**
- ⏳ Server deployment (your next step!)
- ⏳ Apple Shortcuts creation

**Upcoming:**
- 📅 Smart parsers (after data collection)
- 📅 Email reporting
- 📅 Web dashboard
- 📅 Goals & alerts

---

## 🚀 Let's Get Started!

**Right now, do this:**

1. Open [QUICKSTART.md](QUICKSTART.md)
2. Follow Section 2: Install Tailscale
3. Come back here when done

**Estimated time to fully deploy:** 1-2 hours

**You'll have:**
- ✅ Secure remote access to your server
- ✅ Working budget API running 24/7
- ✅ Public webhook for iPhone
- ✅ Professional development setup
- ✅ No router problems ever again!

---

**Good luck! 🎉**

*Questions? Check the troubleshooting sections in each guide.*
