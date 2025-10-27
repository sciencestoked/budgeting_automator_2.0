# Budget Automation System 2.0

A fully automated, zero-friction budgeting system that captures transactions via Apple ecosystem, processes data automatically, and delivers beautiful insights.

## Features

- 📱 **Apple Shortcuts Integration** - Capture transactions from notifications and emails
- 🔄 **Smart Deduplication** - Hash-based duplicate detection
- 🏷️ **Auto-Categorization** - Rule-based transaction categorization
- 📊 **Beautiful Dashboard** - React-based web interface (coming soon)
- 📧 **Email Reports** - Daily/weekly/monthly summaries (coming soon)
- 🎯 **Goals & Alerts** - Track savings goals and spending thresholds
- 🏠 **Self-Hosted** - Runs on your own Ubuntu server

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run the API

```bash
cd backend
source venv/bin/activate
python -m app.main
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 4. Test the Webhook

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rakuten_card",
    "timestamp": "2025-10-27T14:30:00+09:00",
    "vendor": "Family Mart",
    "amount": 1250,
    "currency": "JPY",
    "payment_method": "credit_card",
    "raw_text": "Test transaction"
  }'
```

## Project Structure

```
budgeting_automator_2.0/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── crud.py              # Database operations
│   │   ├── categorization.py   # Auto-categorization
│   │   ├── deduplication.py    # Duplicate detection
│   │   ├── database.py          # DB connection
│   │   └── config.py            # Settings
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # Coming soon
├── shortcuts/                   # Coming soon
├── PROJECT_PLAN.md             # Detailed project plan
└── README.md                    # This file
```

## API Endpoints

### Webhook
- `POST /api/webhook` - Receive transaction from Apple Shortcuts

### Transactions
- `GET /api/transactions` - List transactions (with filters)
- `GET /api/transactions/{id}` - Get specific transaction
- `GET /api/summary` - Get spending summary

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category

### Goals
- `GET /api/goals` - List goals
- `POST /api/goals` - Create goal

### Alerts
- `GET /api/alerts` - List alerts
- `POST /api/alerts` - Create alert

## Development Status

✅ **Phase 1: MVP Backend** - Complete
- [x] FastAPI setup
- [x] Database models
- [x] Webhook endpoint
- [x] Deduplication logic
- [x] Auto-categorization

⏳ **Phase 2: Apple Shortcuts** - Next
- [ ] Email parsing shortcuts
- [ ] Notification parsing shortcuts

🔜 **Phase 3+** - Upcoming
- [ ] Email reporting
- [ ] Web dashboard
- [ ] Goals & alerts

## Documentation

- [Project Plan](PROJECT_PLAN.md) - Complete architecture and implementation plan
- [API Docs](http://localhost:8000/docs) - Interactive API documentation (when running)

## License

MIT License - Free for personal use

## Author

S. Singhal - 2025
