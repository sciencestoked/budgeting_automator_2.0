# Budget Automation System - Project Plan

**Last Updated:** 2025-10-27
**Status:** Planning & Architecture Phase
**Version:** 2.0 (Complete Redesign)

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Data Flow](#data-flow)
5. [Implementation Phases](#implementation-phases)
6. [Current Progress](#current-progress)
7. [Known Limitations & Workarounds](#known-limitations--workarounds)

---

## Project Overview

### Context
Previously built a Python-based email scraper that:
- Searched emails from Japan Post
- Used regex to extract vendor and amount
- Logged to CSV → Google Sheets
- Manually categorized transactions

**Problem:** System deleted, deemed inefficient due to manual triggers and delayed credit card notifications.

### New Vision
A fully automated, zero-friction budgeting system that:
- **Captures** all transactions via Apple ecosystem (notifications + emails)
- **Processes** data automatically (deduplication, categorization)
- **Delivers** beautiful daily/weekly/monthly summaries via email
- **Visualizes** spending through a self-hosted web dashboard
- **Alerts** on thresholds and goals
- **Runs** 24/7 on home Ubuntu server

### Payment Sources
1. **Rakuten Card** (credit card - Apple Wallet)
2. **PayPay** (mobile payment - app notifications)
3. **Suica** (transit card - Apple Wallet)
4. **Japan Post Bank** (bank transfers - email notifications)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        IPHONE (Data Sources)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   PayPay     │  │   Rakuten    │  │    Suica     │          │
│  │     App      │  │  Card (Mail) │  │ (Apple Pay)  │          │
│  │Notifications │  │   + Gmail    │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┼──────────────────┘                   │
│                           ▼                                      │
│                 ┌────────────────────┐                           │
│                 │ Apple Shortcuts    │                           │
│                 │  (Manual Trigger)  │                           │
│                 │  - Parse Email     │                           │
│                 │  - Extract Regex   │                           │
│                 │  - Format JSON     │                           │
│                 └─────────┬──────────┘                           │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTPS Webhook (POST JSON)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    UBUNTU SERVER (Home Laptop)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Backend API (FastAPI/Flask)             │  │
│  │  - Webhook endpoint to receive transactions               │  │
│  │  - Data validation & sanitization                         │  │
│  │  - Deduplication logic (hash-based)                       │  │
│  │  - Auto-categorization (rules engine + ML optional)       │  │
│  │  - Scheduled jobs (daily/weekly/monthly reports)          │  │
│  │  - Email service (SMTP for newsletters)                   │  │
│  │  - REST API for web dashboard                             │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │              Database (PostgreSQL/SQLite)                 │  │
│  │  Tables:                                                  │  │
│  │  - transactions (id, date, vendor, amount, category, etc)│  │
│  │  - categories (id, name, budget_limit, color)            │  │
│  │  - goals (id, target, current, deadline)                 │  │
│  │  - alerts (id, threshold, type, active)                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │           Web Dashboard (React/Vue/Svelte + Tailwind)     │  │
│  │  - Beautiful, intuitive UI                                │  │
│  │  - Date range filters                                      │  │
│  │  - Category breakdowns (charts, graphs)                   │  │
│  │  - Goal tracking visualizations                           │  │
│  │  - Transaction list with search/filter                    │  │
│  │  - Google Sign-In (future: multi-user)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Scheduled Services (Cron/APScheduler)        │  │
│  │  - Daily summary email (8 AM)                             │  │
│  │  - Weekly summary email (Monday 8 AM)                     │  │
│  │  - Monthly summary email (1st of month 8 AM)              │  │
│  │  - Threshold alerts (real-time)                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Mobile Layer (iPhone)
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Email Client | Gmail App | Receive transaction emails from Japan Post, Rakuten |
| Payment Apps | PayPay, Suica (Apple Pay) | Generate transaction notifications |
| Automation | **Apple Shortcuts** | Parse emails/notifications, extract data, send to server |
| Network | HTTPS Webhook | POST JSON data to server endpoint |

**Note:** Apple Shortcuts email automations require manual confirmation (iOS limitation). User must tap to trigger.

### Server Layer (Ubuntu Laptop)
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend Framework** | **FastAPI** | Fast, async, automatic API docs, type hints |
| **Database** | **PostgreSQL** (production) or **SQLite** (MVP) | Robust, relational, ACID compliant |
| **ORM** | **SQLAlchemy** | Python ORM with migrations (Alembic) |
| **Task Scheduler** | **APScheduler** or **Celery** | Cron jobs for daily/weekly/monthly emails |
| **Email Service** | **SMTP (SendGrid/Mailgun)** or local SMTP | Send newsletter-style summaries |
| **Web Server** | **Nginx** (reverse proxy) + **Uvicorn** (ASGI) | Production-ready deployment |
| **Authentication** | **OAuth2 (Google Sign-In)** | Future multi-user support |

### Frontend Layer (Web Dashboard)
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | **React** with **Vite** | Fast, modern, huge ecosystem |
| **Styling** | **Tailwind CSS** + **shadcn/ui** | Beautiful, customizable components |
| **Charts** | **Recharts** or **Chart.js** | Interactive visualizations |
| **State Management** | **Zustand** or **React Query** | Lightweight, async-friendly |
| **Auth** | **Google OAuth 2.0** | Secure, standard |
| **Hosting** | Self-hosted on Ubuntu server | Same machine as backend |

### DevOps & Utilities
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Process Manager | **systemd** or **PM2** | Keep services running 24/7 |
| Reverse Proxy | **Nginx** | Route traffic, SSL termination |
| SSL Certificate | **Let's Encrypt** (Certbot) | HTTPS for webhook security |
| Logging | **Python logging** + **Logrotate** | Debug and monitor |
| Version Control | **Git** + **GitHub** | Code versioning |

---

## Data Flow

### 1. Transaction Capture
```
Transaction occurs → Notification/Email arrives → User opens Shortcuts →
Manual tap to run automation → Shortcut parses data → Extracts:
  - Date/Time
  - Vendor name
  - Amount
  - Payment method (PayPay/Rakuten/Suica/Bank)
  - Raw text (for debugging)
→ Formats as JSON → POSTs to server webhook
```

**Sample JSON Payload:**
```json
{
  "source": "rakuten_card",
  "timestamp": "2025-10-27T14:30:00+09:00",
  "vendor": "Family Mart",
  "amount": 1250,
  "currency": "JPY",
  "raw_text": "ご利用ありがとうございます。Family Martで1,250円のお支払いがありました。",
  "payment_method": "credit_card"
}
```

### 2. Server Processing
```
Webhook receives POST → Validate JSON schema →
Calculate transaction hash (vendor + amount + timestamp) →
Check database for duplicate → If unique:
  - Insert into transactions table
  - Apply categorization rules (regex/keyword matching)
  - Check threshold alerts
  - Send real-time alert if triggered
```

### 3. Categorization Logic
**Rule-based (Phase 1):**
```python
CATEGORY_RULES = {
    "food_snack": ["Family Mart", "Lawson", "7-Eleven", "Starbucks"],
    "utilities": ["Japan Post", "NTT", "Tokyo Electric"],
    "shopping": ["Amazon", "Rakuten Ichiba", "Uniqlo"],
    "transport": ["Suica", "JR East", "Metro"],
}
```

**ML-based (Phase 2 - Future):**
- Train on historical labeled data
- Use vendor name + amount as features
- Auto-categorize new transactions

### 4. Report Generation
**Daily Summary (8 AM):**
- Total spent yesterday
- Top 3 categories
- Comparison with daily average
- Mini bar chart (text/HTML email)

**Weekly Summary (Monday 8 AM):**
- Total spent this week
- Category breakdown (pie chart)
- Week-over-week comparison
- Goal progress update

**Monthly Summary (1st of month 8 AM):**
- Total spent this month
- Full category breakdown with budgets
- Goal achievements
- Spending trends (line graph)
- Top vendors

**Email Format:** HTML newsletter with inline CSS (responsive, mobile-friendly)

### 5. Web Dashboard Access
```
User opens browser → Navigate to https://your-server-ip:PORT →
Google Sign-In → Dashboard loads:
  - Summary cards (total, categories, goals)
  - Date range picker (today, week, month, custom)
  - Interactive charts (filter by category, vendor)
  - Transaction table (search, sort, export CSV)
  - Settings (manage categories, goals, thresholds)
```

---

## Implementation Phases

### Phase 0: Environment Setup ✅ (Current)
- [x] Create project directory structure
- [ ] Set up Git repository
- [ ] Document project plan (this file)
- [ ] Install Python, Node.js on Ubuntu server
- [ ] Configure server network (static IP, port forwarding)
- [ ] Set up SSL certificate (Let's Encrypt) for HTTPS webhook

### Phase 1: MVP Backend (Week 1-2)
**Goal:** Receive transactions, store in database, basic deduplication

- [ ] Create FastAPI project structure
- [ ] Design database schema (SQLAlchemy models)
- [ ] Implement webhook endpoint (`POST /api/transactions`)
- [ ] Add JSON validation (Pydantic models)
- [ ] Implement deduplication logic (hash-based)
- [ ] Set up SQLite database (easy to migrate to PostgreSQL later)
- [ ] Add basic logging
- [ ] Test with curl/Postman

**Deliverable:** Working API that stores transactions

### Phase 2: Apple Shortcuts Integration (Week 2)
**Goal:** Send real transaction data from iPhone to server

- [ ] Research email parsing regex for Japan Post, Rakuten Card
- [ ] Create Apple Shortcut: Parse Email → Extract Data → POST to webhook
- [ ] Create Apple Shortcut: Parse PayPay notification (if possible)
- [ ] Handle Suica transactions (Apple Pay notifications)
- [ ] Test end-to-end: Transaction → Email → Shortcut → Server → Database
- [ ] Debug and refine parsing logic

**Deliverable:** Automated transaction logging from all sources

### Phase 3: Categorization & Deduplication (Week 3)
**Goal:** Smart categorization and robust duplicate detection

- [ ] Implement rule-based categorization engine
- [ ] Create category management endpoints (CRUD)
- [ ] Improve deduplication (fuzzy matching for vendor names)
- [ ] Add manual categorization override endpoint
- [ ] Build admin CLI for bulk categorization

**Deliverable:** Transactions auto-categorized correctly

### Phase 4: Email Reporting (Week 4)
**Goal:** Daily/weekly/monthly email summaries

- [ ] Set up SMTP email service (SendGrid free tier or local)
- [ ] Design HTML email templates (responsive)
- [ ] Implement report generation logic (aggregate queries)
- [ ] Set up APScheduler for cron jobs
- [ ] Test daily summary email
- [ ] Test weekly summary email
- [ ] Test monthly summary email

**Deliverable:** Automated email newsletters

### Phase 5: Web Dashboard - Backend (Week 5)
**Goal:** REST API for dashboard

- [ ] Create API endpoints:
  - `GET /api/transactions` (with filters)
  - `GET /api/summary` (date range, category breakdown)
  - `GET /api/goals`
  - `POST /api/goals`
  - `GET /api/categories`
- [ ] Implement Google OAuth 2.0 backend
- [ ] Add JWT token authentication
- [ ] Document API with FastAPI auto-docs

**Deliverable:** Complete REST API

### Phase 6: Web Dashboard - Frontend (Week 6-7)
**Goal:** Beautiful, intuitive UI

- [ ] Set up React + Vite project
- [ ] Install Tailwind CSS + shadcn/ui
- [ ] Implement Google Sign-In (frontend)
- [ ] Build pages:
  - Dashboard (summary cards, charts)
  - Transactions (table with filters)
  - Goals (progress bars, forms)
  - Settings (categories, thresholds)
- [ ] Integrate Recharts for visualizations
- [ ] Make responsive (mobile-friendly)
- [ ] Test on multiple devices

**Deliverable:** Fully functional web dashboard

### Phase 7: Goals & Alerts (Week 8)
**Goal:** Proactive budget management

- [ ] Implement goal tracking (save X by Y date)
- [ ] Add threshold alerts (email + push notification via Pushcut?)
- [ ] Build goal visualization UI
- [ ] Test alert triggers

**Deliverable:** Goal tracking and alerts working

### Phase 8: Deployment & Optimization (Week 9)
**Goal:** Production-ready system

- [ ] Migrate SQLite → PostgreSQL (if needed)
- [ ] Set up Nginx reverse proxy
- [ ] Configure systemd services for auto-restart
- [ ] Add log rotation
- [ ] Optimize database queries (indexes)
- [ ] Add backup scripts (daily DB dumps)
- [ ] Test disaster recovery

**Deliverable:** 24/7 running system on Ubuntu server

### Phase 9: Polish & Future Features (Ongoing)
**Optional Enhancements:**
- [ ] Mobile app (React Native) for on-the-go access
- [ ] OCR receipt scanning
- [ ] Export data (CSV, PDF reports)
- [ ] Multi-currency support
- [ ] Budgeting recommendations (AI-powered)
- [ ] Shared budgets (multi-user with Google Sign-In)
- [ ] Dark mode UI
- [ ] Voice assistant integration ("Hey Siri, how much did I spend today?")

---

## Current Progress

**Phase:** 0 - Environment Setup
**Completed Tasks:**
- ✅ Project plan documentation created

**Next Steps:**
1. Set up Git repository
2. Configure Ubuntu server networking
3. Install dependencies (Python, Node.js, PostgreSQL)
4. Obtain SSL certificate for webhook HTTPS

**Blockers:** None

---

## Known Limitations & Workarounds

### Limitation 1: Apple Shortcuts Email Automation Not Fully Automatic
**Issue:** iOS requires manual confirmation for email-triggered shortcuts (privacy/security).

**Workarounds:**
1. **Manual Trigger (Recommended for MVP):**
   - User taps notification → Runs shortcut
   - Pros: Simple, works immediately
   - Cons: Requires daily discipline

2. **Pushcut + Automation Server (Advanced):**
   - Run Pushcut Automation Server on Mac/iPad at home
   - iOS shortcuts trigger server actions automatically
   - Server sends data to Ubuntu server
   - Pros: Truly automated
   - Cons: Requires additional hardware (iPad/Mac always on)

3. **IFTTT Webhooks (Alternative):**
   - IFTTT monitors Gmail
   - Triggers webhook on new email from specific senders
   - Pros: No manual trigger
   - Cons: Less flexible parsing, free tier limits, third-party dependency

**Decision:** Start with Manual Trigger (MVP), upgrade to Pushcut if needed.

### Limitation 2: Credit Card Notifications Delayed (Day Late)
**Issue:** Rakuten Card emails arrive next day.

**Workaround:**
- Accept delay as inherent to the system
- Use daily summaries to review previous day's spending
- For real-time tracking, rely on PayPay/Suica (instant notifications)

### Limitation 3: Duplicate Transactions Across Sources
**Issue:** Same transaction might appear in both Apple Pay notification AND email.

**Deduplication Strategy:**
1. Generate hash: `SHA256(vendor + amount + date + source)`
2. Before insert, check if hash exists in DB (within 24-hour window)
3. If duplicate detected:
   - Log as duplicate
   - Keep first occurrence
   - Update `duplicate_count` field
4. For fuzzy matching (vendor name variations):
   - Use Levenshtein distance (e.g., "Family Mart" vs "FamilyMart")
   - Threshold: 80% similarity

### Limitation 4: Server Accessibility from Internet
**Issue:** Home server behind NAT, dynamic IP.

**Solutions:**
1. **Port Forwarding:**
   - Configure router to forward port 443 → Ubuntu server
   - Pros: Simple, no cost
   - Cons: Security risk, requires static IP or DDNS

2. **Dynamic DNS (DDNS):**
   - Use No-IP, DuckDNS for free subdomain
   - Update IP automatically with cron script
   - Pros: Works with dynamic IP
   - Cons: Free subdomains may expire

3. **Cloudflare Tunnel (Recommended):**
   - Free, secure tunnel without port forwarding
   - HTTPS automatically
   - Pros: Secure, easy setup, no exposed ports
   - Cons: Requires Cloudflare account

4. **Tailscale VPN (Alternative):**
   - Create private network (iPhone ↔ Server)
   - Pros: Secure, no public exposure
   - Cons: iPhone must be on VPN to send data

**Decision:** Use Cloudflare Tunnel for webhook, Tailscale for dashboard access (extra security).

---

## Development Guidelines

### Code Style
- **Python:** PEP 8, type hints, docstrings
- **JavaScript/React:** ESLint + Prettier, functional components
- **Commits:** Conventional Commits format (`feat:`, `fix:`, `docs:`)

### Testing
- **Backend:** Pytest (unit tests for categorization, deduplication)
- **Frontend:** Vitest + React Testing Library
- **Integration:** Test webhook → DB → API → Frontend flow

### Documentation
- **API:** Auto-generated with FastAPI (Swagger UI)
- **Codebase:** Inline comments for complex logic
- **User Guide:** Markdown file for setup and usage

### Security
- **Secrets:** Use `.env` file (never commit), environment variables
- **API:** HTTPS only, rate limiting (prevent spam)
- **Auth:** Secure JWT tokens, Google OAuth 2.0
- **Database:** Parameterized queries (prevent SQL injection)

---

## File Structure (Planned)

```
budgeting_automator_2.0/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # DB connection
│   │   ├── crud.py              # Database operations
│   │   ├── auth.py              # OAuth logic
│   │   ├── categorization.py   # Rule engine
│   │   ├── deduplication.py    # Duplicate detection
│   │   ├── email_service.py    # SMTP email sender
│   │   ├── scheduler.py         # APScheduler jobs
│   │   └── config.py            # Environment config
│   ├── tests/
│   ├── alembic/                 # DB migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── shortcuts/
│   ├── rakuten_email_parser.shortcut  # (export for sharing)
│   ├── paypay_parser.shortcut
│   └── README.md                      # Setup instructions
├── scripts/
│   ├── backup_db.sh                   # Daily backup cron job
│   └── setup_server.sh                # Server initialization
├── docs/
│   ├── API.md                         # API documentation
│   └── USER_GUIDE.md                  # End-user instructions
├── PROJECT_PLAN.md                    # This file
├── README.md                          # Project overview
└── .gitignore
```

---

## Resources & References

### Apple Shortcuts
- [Apple Shortcuts User Guide](https://support.apple.com/guide/shortcuts/welcome/ios)
- [Making HTTP Requests in Shortcuts](https://support.apple.com/guide/shortcuts/request-your-first-api-apd58d46713f/ios)
- [Shortcuts Community (Automators Talk)](https://talk.automators.fm/)

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)

### React + Tailwind
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui Components](https://ui.shadcn.com/)

### Deployment
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Let's Encrypt Certbot](https://certbot.eff.org/)
- [systemd Service Tutorial](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

## Contact & Collaboration

**Primary Developer:** S. Singhal
**Project Start Date:** 2025-10-27
**Repository:** (To be created)

**For AI Assistants:**
- This document is the **single source of truth** for project context
- Update `Current Progress` section after each work session
- Add new discoveries to `Known Limitations & Workarounds`
- Keep implementation phases updated with checkmarks

---

**Note:** This is a living document. Update as the project evolves.
