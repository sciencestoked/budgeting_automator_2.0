# Budget Automator 2.0 - Quick Start Guide

**Last Updated:** 2025-10-27
**Status:** Phase 1 Complete (MVP Backend), Phase 2 Starting (Data Collection)

---

## What's Been Built So Far ✅

### Working Backend API
- FastAPI server with SQLite database
- Webhook endpoint for receiving transactions
- Auto-categorization (rule-based)
- Duplicate detection (hash-based)
- Raw data collection for analysis
- Pending clarifications system

---

## How to Resume Work

### 1. Start the Backend Server

```bash
cd /Users/s-singhal/budgeting_automator_2.0/backend
source venv/bin/activate
python -m app.main
```

Server runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 2. Deploy to Ubuntu Server (When Ready)

```bash
# On Ubuntu server:
cd ~
git clone <your-repo-url>
cd budgeting_automator_2.0/backend

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your settings

# Run with systemd (persistent)
sudo nano /etc/systemd/system/budget-api.service
```

**systemd service file:**
```ini
[Unit]
Description=Budget Automation API
After=network.target

[Service]
User=your-username
WorkingDirectory=/home/your-username/budgeting_automator_2.0/backend
Environment="PATH=/home/your-username/budgeting_automator_2.0/backend/venv/bin"
ExecStart=/home/your-username/budgeting_automator_2.0/backend/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable budget-api
sudo systemctl start budget-api
sudo systemctl status budget-api
```

### 3. Set Up Cloudflare Tunnel (Free, Secure)

**Why:** Makes your home server accessible from iPhone without opening ports

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create budget-automation

# Configure tunnel
nano ~/.cloudflared/config.yml
```

**config.yml:**
```yaml
url: http://localhost:8000
tunnel: <your-tunnel-id>
credentials-file: /home/your-username/.cloudflared/<tunnel-id>.json
```

```bash
# Run tunnel
cloudflared tunnel route dns budget-automation budget.yourdomain.com
cloudflared tunnel run budget-automation
```

Now your API is accessible at: `https://budget.yourdomain.com`

---

## Phase 2: Data Collection Strategy

### Week 1: Discovery - Collect Raw Data

**Goal:** Understand what data you can actually extract from different sources

#### Step 1: Create a Simple Data Dumper Shortcut

1. **Open Shortcuts app** on iPhone
2. **Create New Shortcut** (not automation yet)
3. **Name it:** "Budget Data Dump"

**Shortcut Actions:**
```
[1] Ask for Input
    - Question: "Paste transaction info"
    - Input Type: Text
    ↓
[2] Set Variable "raw_text" = [Provided Input]
    ↓
[3] Get Current Date
    ↓
[4] Set Variable "timestamp" = [Current Date]
    ↓
[5] Dictionary:
    {
      "source": "manual_test",
      "timestamp": "[timestamp]",
      "raw_text": "[raw_text]"
    }
    ↓
[6] Get Contents of URL
    - URL: https://budget.yourdomain.com/api/data-dump
    - Method: POST
    - Headers: Content-Type = application/json
    - Request Body: [Dictionary from step 5]
    ↓
[7] Show Result (to confirm it worked)
```

#### Step 2: Collect Sample Data

**For the next week, whenever you make a transaction:**

1. **Rakuten Card (Email):**
   - Open email notification
   - Copy entire email body
   - Run "Budget Data Dump" shortcut
   - Paste email content

2. **PayPay (Notification):**
   - Long-press notification
   - Select "Copy"
   - Run shortcut
   - Paste notification text

3. **Suica (Manual):**
   - After tapping card, check Wallet app
   - Take screenshot OR manually note: vendor, amount, time
   - Run shortcut
   - Paste info

4. **Japan Post (Email):**
   - Same as Rakuten Card

#### Step 3: Analyze Collected Data

After 1 week, check what you collected:

```bash
curl http://localhost:8000/api/data-dumps | python3 -m json.tool
```

Or visit: `http://localhost:8000/docs` → Try `/api/data-dumps` endpoint

**Look for:**
- ✅ Can we extract vendor name?
- ✅ Can we extract amount?
- ✅ Can we extract datetime?
- ✅ What's the pattern/format?

---

## Phase 3: Build Smart Parsers

### Once You Know the Patterns:

**Example: Rakuten Card Email Parser**

```python
# Add to backend/app/parsers.py (create this file)

import re
from datetime import datetime

def parse_rakuten_email(email_body: str) -> dict:
    """Extract transaction from Rakuten Card email."""

    patterns = {
        'vendor': r'ご利用先[:：]\s*(.+)',
        'amount': r'ご利用金額[:：]\s*([¥\d,]+)円?',
        'date': r'ご利用日[:：]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        'payment_method': r'お支払方法[:：]\s*(.+)'
    }

    result = {}

    # Extract vendor
    match = re.search(patterns['vendor'], email_body)
    if match:
        result['vendor'] = match.group(1).strip()

    # Extract amount
    match = re.search(patterns['amount'], email_body)
    if match:
        amount_str = match.group(1).replace(',', '').replace('¥', '')
        result['amount'] = float(amount_str)

    # Extract date
    match = re.search(patterns['date'], email_body)
    if match:
        year, month, day = match.groups()
        result['timestamp'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}T12:00:00+09:00"

    result['source'] = 'rakuten_card'
    result['payment_method'] = 'credit_card'
    result['currency'] = 'JPY'

    return result
```

---

## Vendor Name Normalization

### The Problem:
Same vendor, many spellings:
- "ファミリーマート" (Katakana)
- "Family Mart" (English)
- "FamilyMart" (No space)
- "Famima" (Nickname)

### Solution: Create Vendor Alias Table

```python
# Add to backend/app/vendor_normalization.py (create this file)

VENDOR_ALIASES = {
    "familymart": {
        "canonical": "Family Mart",
        "aliases": ["family mart", "ファミリーマート", "famima", "famiri-ma-to", "familymart"],
        "category": "food_snack"
    },
    "lawson": {
        "canonical": "Lawson",
        "aliases": ["ローソン", "roson", "lawson"],
        "category": "food_snack"
    },
    "jr_east": {
        "canonical": "JR East",
        "aliases": ["jr東日本", "jr east japan", "東日本旅客鉄道", "jreast"],
        "category": "transport"
    },
}

def normalize_vendor(vendor_raw: str) -> tuple[str, str]:
    """
    Normalize vendor name and suggest category.

    Returns:
        (canonical_name, category)
    """
    vendor_lower = vendor_raw.lower().replace(' ', '').replace('-', '')

    for canonical_key, data in VENDOR_ALIASES.items():
        for alias in data['aliases']:
            alias_clean = alias.lower().replace(' ', '').replace('-', '')
            if alias_clean in vendor_lower or vendor_lower in alias_clean:
                return data['canonical'], data['category']

    # No match found, return original
    return vendor_raw, None
```

---

## Smart Duplicate Detection

### Types of Duplicates:

**1. Same Transaction, Multiple Sources** (COMMON)
```
Email:        Rakuten Card: Family Mart ¥1,250 (arrives tomorrow)
Notification: Apple Pay:    Family Mart ¥1,250 (instant today)
```
→ Same transaction, notified twice

**2. Monthly Bill = Sum of Transactions**
```
Week 1: PayPay ¥500
Week 2: PayPay ¥800
Week 3: PayPay ¥1,200
---
End of Month Email: PayPay Bill ¥2,500
```
→ Bill is a summary, not a new charge

**3. Correction/Refund**
```
Day 1: Charge ¥5,000
Day 2: Refund -¥5,000
```
→ Net zero

### Implementation Strategy:

```python
# Add to backend/app/duplicate_detection.py (create this file)

def calculate_duplicate_probability(tx1: dict, tx2: dict) -> float:
    """
    Calculate probability that two transactions are duplicates.

    Returns:
        Float 0.0-1.0 (0 = different, 1.0 = definite duplicate)
    """
    score = 0.0

    # Exact same hash = 100% duplicate
    if tx1.get('transaction_hash') == tx2.get('transaction_hash'):
        return 1.0

    # Amount match (40% weight)
    if tx1.get('amount') == tx2.get('amount'):
        score += 0.4

    # Vendor similarity (30% weight)
    vendor1 = tx1.get('vendor', '').lower()
    vendor2 = tx2.get('vendor', '').lower()
    similarity = levenshtein_ratio(vendor1, vendor2)
    score += similarity * 0.3

    # Date proximity (20% weight) - within 48 hours
    dt1 = parse_datetime(tx1.get('timestamp'))
    dt2 = parse_datetime(tx2.get('timestamp'))
    hours_apart = abs((dt1 - dt2).total_seconds() / 3600)
    if hours_apart <= 48:
        date_score = 1.0 - (hours_apart / 48)
        score += date_score * 0.2

    # Different sources = likely duplicate (10% weight)
    # Email + notification of same thing
    source1 = tx1.get('source', '')
    source2 = tx2.get('source', '')
    if 'email' in source1 and 'notification' in source2:
        score += 0.1
    elif 'email' in source2 and 'notification' in source1:
        score += 0.1

    return min(score, 1.0)


def should_flag_for_review(probability: float) -> bool:
    """Decide if user should review this potential duplicate."""
    return 0.5 <= probability < 0.8  # Medium confidence


def should_auto_merge(probability: float) -> bool:
    """Decide if we should automatically mark as duplicate."""
    return probability >= 0.8  # High confidence
```

---

## Pending Clarifications System

### When to Flag Transactions for User Review:

1. **Unknown Vendor** - Vendor not in normalization table
2. **Low Category Confidence** - Can't determine category
3. **Potential Duplicate** - 50-80% confidence
4. **Unusual Amount** - 10x higher than vendor average
5. **Negative Amount** - Possible refund

### API Endpoints:

**Get pending clarifications:**
```bash
GET /api/clarifications?resolved=false
```

**Resolve clarification:**
```bash
POST /api/clarifications/{id}/resolve
{
  "action": "confirm",  # or "merge", "recategorize", "ignore"
  "new_category": "food_snack",  # if recategorize
  "merge_with_id": 123  # if merge
}
```

---

## Email Reporting (Phase 4)

### Daily Summary Email (8 AM)

Create: `backend/app/email_service.py`

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings

def send_daily_summary(transactions: list, total: float):
    """Send daily spending summary email."""

    html = f"""
    <html>
      <body>
        <h2>💰 Daily Spending Summary</h2>
        <p><strong>Total Spent:</strong> ¥{total:,.0f}</p>
        <h3>Transactions:</h3>
        <ul>
        {''.join(f'<li>{tx["vendor"]}: ¥{tx["amount"]:,.0f}</li>' for tx in transactions)}
        </ul>
      </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Daily Budget Summary - ¥{total:,.0f}'
    msg['From'] = settings.email_from
    msg['To'] = settings.email_to

    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
```

**Schedule with APScheduler:**

```python
# In backend/app/scheduler.py (create this file)

from apscheduler.schedulers.background import BackgroundScheduler
from .email_service import send_daily_summary
from .crud import get_transactions, get_total_spent
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def daily_summary_job():
    """Run every day at 8 AM."""
    from .database import SessionLocal

    db = SessionLocal()
    yesterday = datetime.now() - timedelta(days=1)
    start_of_yesterday = yesterday.replace(hour=0, minute=0, second=0)
    end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59)

    transactions = get_transactions(db, start_date=start_of_yesterday, end_date=end_of_yesterday)
    total = get_total_spent(db, start_date=start_of_yesterday, end_date=end_of_yesterday)

    send_daily_summary(transactions, total)
    db.close()

# Schedule job
scheduler.add_job(daily_summary_job, 'cron', hour=8, minute=0)
scheduler.start()
```

---

## Current API Endpoints

### Transaction Management
- `POST /api/webhook` - Receive transaction from shortcuts
- `GET /api/transactions` - List all transactions (with filters)
- `GET /api/transactions/{id}` - Get specific transaction
- `GET /api/summary` - Get spending summary

### Data Collection (Discovery Phase)
- `POST /api/data-dump` - Send ANY raw data for analysis
- `GET /api/data-dumps` - View collected raw data

### Clarifications
- `GET /api/clarifications` - Get transactions needing review
- `POST /api/clarifications/{id}/resolve` - User resolves issue

### Categories, Goals, Alerts
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category
- `GET /api/goals` - List goals
- `POST /api/goals` - Create goal
- `GET /api/alerts` - List alerts
- `POST /api/alerts` - Create alert

---

## Next Steps Checklist

### Immediate (This Week):
- [ ] Deploy backend to Ubuntu server
- [ ] Set up Cloudflare Tunnel
- [ ] Create "Budget Data Dump" shortcut
- [ ] Collect 1 week of raw transaction data

### Week 2:
- [ ] Analyze collected data patterns
- [ ] Create regex parsers for each source
- [ ] Build vendor normalization table
- [ ] Implement smart duplicate detection

### Week 3:
- [ ] Create real Apple Shortcuts (email automation)
- [ ] Test end-to-end: Transaction → Email → Shortcut → Server → DB
- [ ] Add pending clarifications UI logic

### Week 4:
- [ ] Implement email reporting (daily/weekly/monthly)
- [ ] Set up APScheduler
- [ ] Test full workflow for 1 week

### Month 2:
- [ ] Build web dashboard (React + Tailwind)
- [ ] Add goals and alerts functionality
- [ ] Polish and optimize

---

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
kill <PID>

# Check logs
journalctl -u budget-api -f
```

### Database issues
```bash
# Delete and recreate
rm backend/budgeting.db
python -m app.main  # Will recreate tables
```

### Shortcuts not connecting
- Check server is accessible: `curl http://your-server/`
- Verify Cloudflare Tunnel is running
- Check iOS allows HTTP requests (Settings → Shortcuts → Advanced)

---

## Files Reference

**Key Files:**
- `PROJECT_PLAN.md` - Complete architecture and roadmap
- `DATA_EXTRACTION_GUIDE.md` - Detailed shortcut creation guide
- `backend/app/main.py` - API endpoints
- `backend/app/models.py` - Database schema
- `backend/app/categorization.py` - Auto-categorization rules
- `backend/app/deduplication.py` - Duplicate detection logic

**To Create Later:**
- `backend/app/parsers.py` - Email/notification parsers
- `backend/app/vendor_normalization.py` - Vendor name cleanup
- `backend/app/duplicate_detection.py` - Smart duplicate matching
- `backend/app/email_service.py` - Email reporting
- `backend/app/scheduler.py` - Scheduled jobs

---

## Contact & Notes

**Project Started:** 2025-10-27
**Current Phase:** 2 (Data Collection)
**Next Milestone:** 1 week of raw data collected

**Remember:**
- Start small - collect data first, optimize later
- iOS has limitations - work around them creatively
- Document everything as you discover patterns
- The vendor name problem is HARD - iterate on it

Good luck! 🚀
