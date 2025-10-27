# Apple Automation Data Extraction Guide

**Goal:** Capture ALL available data from transactions to analyze what we can extract

---

## Phase 1: Discovery - What Data Can We Extract?

### Step 1: Create a "Data Dumper" Shortcut

This shortcut will capture EVERYTHING from a notification/email and send it to your server for analysis.

**Purpose:**
- See exactly what data iOS provides
- Understand differences between: emails, app notifications, Wallet notifications
- Identify patterns for parsing

---

## Creating the Data Dumper Shortcut

### Option A: For App Notifications (PayPay, etc.)

1. **Open Shortcuts app** on iPhone
2. **Create New Automation**
   - Tap "Automation" tab → "+" → "Create Personal Automation"
   - **Trigger:** "App"
   - Select your payment apps: PayPay, Suica app, etc.
   - Choose: "Is Opened" or "Receives Notification" (if available)

3. **Add Actions:**
   ```
   [1] Get Contents of Clipboard
       ↓
   [2] Set Variable: "raw_data" = [Output of step 1]
       ↓
   [3] Get Current Date
       ↓
   [4] Set Variable: "timestamp" = [Output of step 3]
       ↓
   [5] Text:
       {
         "source": "paypay_notification",
         "timestamp": "[timestamp]",
         "raw_data": "[raw_data]",
         "full_notification": "MANUALLY_PASTE_HERE"
       }
       ↓
   [6] Get Contents of URL
       - URL: http://YOUR_SERVER_IP:8000/api/data-dump
       - Method: POST
       - Headers: Content-Type = application/json
       - Request Body: [Output of step 5]
   ```

**Problem:** iOS doesn't give shortcuts direct access to notification content! 😤

**Workaround:**
- When you get a notification, **long-press** → **Copy**
- Then manually run the shortcut
- Or take a **screenshot** and we'll extract from that

---

### Option B: For Emails (Japan Post, Rakuten Card)

1. **Open Shortcuts app**
2. **Create New Automation**
   - Tap "Automation" → "+" → "Create Personal Automation"
   - **Trigger:** "Email"
   - **From:** Enter sender email (e.g., `noreply@rakuten-card.co.jp`)
   - **Subject Contains:** (optional, like "ご利用" or "お支払い")

3. **Add Actions:**
   ```
   [1] Get Latest Email (from trigger)
       ↓
   [2] Get Details of Email
       - Get: Sender, Subject, Date, Body (plain text)
       ↓
   [3] Set Variable: "email_body" = Body
       ↓
   [4] Set Variable: "email_subject" = Subject
       ↓
   [5] Set Variable: "email_date" = Date
       ↓
   [6] Text:
       {
         "source": "email_rakuten_card",
         "timestamp": "[email_date]",
         "subject": "[email_subject]",
         "body": "[email_body]",
         "data_type": "raw_dump"
       }
       ↓
   [7] Get Contents of URL
       - URL: http://YOUR_SERVER_IP:8000/api/data-dump
       - Method: POST
       - Headers: Content-Type = application/json
       - Request Body: [Output of step 6]
   ```

**Note:** You'll need to tap "Run" when the notification appears (iOS limitation)

---

### Option C: For Wallet/Suica Card Taps

**Bad News:** Apple doesn't expose Wallet transaction details to Shortcuts directly.

**Available Data from Wallet Notifications:**
- ❌ Transaction amount (not accessible)
- ❌ Merchant name (not accessible)
- ✅ Card name (e.g., "Suica")
- ✅ Date/time of notification

**Workarounds:**
1. **Screenshot Method:**
   - When you see Wallet notification, take screenshot
   - Use OCR (Optical Character Recognition) shortcut
   - Extract text and send to server

2. **Manual Copy-Paste:**
   - Long-press notification → Copy
   - Run shortcut to send copied text to server

3. **Email Fallback:**
   - Many transit cards (Suica) send **monthly summaries** via email
   - Parse those instead of real-time notifications

---

## Data Collection Endpoint Setup

Let's add a `/api/data-dump` endpoint to collect raw data:

### What It Does:
- Receives ANY JSON with raw text
- Stores it in a separate `raw_data` table
- Allows you to analyze patterns later
- No validation - accepts everything

### Fields We'll Capture:
```json
{
  "source": "string (email/notification/screenshot)",
  "timestamp": "ISO datetime",
  "raw_text": "THE ENTIRE CONTENT",
  "metadata": {
    "email_subject": "if email",
    "sender": "if email",
    "app_name": "if app notification",
    "screenshot_path": "if OCR"
  }
}
```

---

## What Data CAN We Extract? (By Source)

### 1. **Email (Japan Post, Rakuten Card Bills)**

**Available Fields:**
- ✅ **Vendor/Merchant Name** - From email body
- ✅ **Amount** - Regex: `¥?\d{1,3}(,\d{3})*円?`
- ✅ **Date** - Email date or parsed from body
- ✅ **Payment Method** - Inferred from sender
- ✅ **Bill Period** - For monthly statements
- ✅ **Previous Balance** - For credit card bills
- ✅ **Current Balance** - For credit card bills
- ✅ **Full Transaction List** - If monthly summary

**Example Rakuten Card Email Pattern:**
```
件名: 【楽天カード】ご利用明細のお知らせ
本文:
ご利用日: 2025年10月27日
ご利用先: ファミリーマート
ご利用金額: 1,250円
お支払方法: 1回払い
```

**Regex Patterns:**
- Vendor: `ご利用先[:：]\s*(.+)`
- Amount: `ご利用金額[:：]\s*([¥\d,]+)円?`
- Date: `ご利用日[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日)`

---

### 2. **App Notifications (PayPay)**

**Available Fields (LIMITED):**
- ⚠️ **Notification Text Only** - Usually short summary
- ✅ **Amount** - If shown in notification
- ✅ **Vendor** - If shown in notification
- ❌ **Full Details** - Must open app
- ⚠️ **Datetime** - Notification time (may differ from transaction time)

**Example PayPay Notification:**
```
"ファミリーマートで1,250円のお支払い"
```

**Extraction:**
- Vendor: `(.+)で`
- Amount: `([¥\d,]+)円`

**Problem:** iOS doesn't let Shortcuts read notification content automatically!

**Best Practice:**
- Use PayPay **email receipts** if enabled
- Or manually copy notification text when it appears

---

### 3. **Wallet/Suica Card Taps**

**Available Fields (VERY LIMITED):**
- ❌ **Amount** - Not accessible via shortcuts
- ❌ **Vendor/Station** - Not accessible
- ✅ **Card Name** - "Suica"
- ✅ **Datetime** - Notification time

**Reality Check:**
Apple locks down Wallet data for privacy. You CANNOT get transaction details via Shortcuts.

**Alternative Solutions:**
1. **Suica Email Summaries** - JR East sends monthly usage reports
2. **Suica App History** - Manual export (not automatable)
3. **OCR from Screenshots** - Take screenshot → extract text
4. **Accept Limitation** - Track Suica separately or ignore

---

### 4. **Manual Entry (Widget/Share Sheet)**

**Best Option for Card Taps!**

Create a quick-entry shortcut:
- Add to Home Screen widget
- Tap → Enter amount & vendor
- Instantly sends to server

**Available Fields (ALL):**
- ✅ Vendor (you type)
- ✅ Amount (you type)
- ✅ Category (optional dropdown)
- ✅ Payment method (auto-filled)
- ✅ Timestamp (automatic)

---

## Recommended Data Collection Strategy

### Week 1: Discovery Phase

**Goal:** Collect ALL raw data from different sources

1. **Create 3 separate "dumper" shortcuts:**
   - `Email Dumper` (for Rakuten, Japan Post)
   - `Notification Dumper` (for PayPay, when you copy text)
   - `Manual Entry` (for Suica, quick purchases)

2. **For 1 week, send EVERYTHING to `/api/data-dump`:**
   - Every transaction email
   - Every notification you copy
   - Every Suica tap (manual entry)

3. **Analyze the collected data:**
   - Look for patterns in vendor names
   - Find regex patterns that work
   - Identify edge cases

### Week 2: Build Real Parsers

Based on Week 1 analysis:
- Create vendor name normalization rules
- Build smart duplicate detection
- Set up confidence scoring

---

## Handling Japanese Vendor Names

### The Problem:
```
Same Vendor, Multiple Spellings:
- ファミリーマート (Katakana)
- Family Mart (English)
- FamilyMart (No space)
- Famima (Nickname)
- familymart (Lowercase)
```

### Solution: Vendor Normalization Table

```python
VENDOR_ALIASES = {
    "familymart": ["family mart", "ファミリーマート", "famima", "famiri-ma-to"],
    "lawson": ["ローソン", "roson"],
    "seven_eleven": ["7-eleven", "7-11", "セブンイレブン", "sebun"],
    "jr_east": ["jr東日本", "jr east japan", "東日本旅客鉄道"],
}
```

**Strategy:**
1. Convert to lowercase
2. Remove spaces/hyphens
3. Convert katakana to romaji (using library)
4. Match against alias table
5. Store canonical name in DB

---

## Smart Duplicate Detection

### Types of Duplicates:

**Type 1: Same Transaction, Multiple Sources**
```
[Email]        Rakuten Card: Family Mart ¥1,250 (arrives next day)
[Notification] Apple Pay: Family Mart ¥1,250 (instant)
```
**Detection:** Same amount + vendor + date → High confidence duplicate

**Type 2: Monthly Bill vs Individual Transactions**
```
[Week 1-4]  Individual: PayPay ¥500, ¥800, ¥1,200
[Month End] Bill Email: PayPay Total ¥2,500
```
**Detection:** Bill = sum of individuals → Tag as "summary", don't double-count

**Type 3: Corrections/Refunds**
```
[Day 1] Charge: ¥5,000
[Day 2] Refund: -¥5,000
```
**Detection:** Same vendor + negative amount → Tag as "refund"

### Confidence Scoring:

```python
def calculate_duplicate_confidence(tx1, tx2):
    score = 0.0

    # Exact match = 100%
    if tx1.hash == tx2.hash:
        return 1.0

    # Amount match
    if tx1.amount == tx2.amount:
        score += 0.4

    # Vendor similarity
    vendor_sim = levenshtein_similarity(tx1.vendor, tx2.vendor)
    score += vendor_sim * 0.3

    # Date proximity (within 48 hours)
    hours_apart = abs(tx1.timestamp - tx2.timestamp).hours
    if hours_apart <= 48:
        score += 0.2 * (1 - hours_apart/48)

    # Payment source (email + notification = likely duplicate)
    if {tx1.source, tx2.source} == {"email", "notification"}:
        score += 0.1

    return score
```

**Thresholds:**
- `> 0.8` = Definite duplicate (auto-merge)
- `0.5 - 0.8` = Possible duplicate (flag for review)
- `< 0.5` = Different transactions

---

## Pending Clarifications System

### When to Flag Transactions:

1. **Low Categorization Confidence:**
   - Unknown vendor
   - Ambiguous category (e.g., "Amazon" could be shopping, groceries, electronics)

2. **Potential Duplicate:**
   - Confidence score 0.5-0.8
   - Same amount, different vendors

3. **Unusual Amount:**
   - 10x higher than vendor average
   - Negative amount (refund?)

4. **Missing Data:**
   - No vendor name extracted
   - Date parsing failed

### Data Structure:

```python
class PendingClarification(Base):
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    issue_type = Column(String)  # 'category', 'duplicate', 'vendor'
    confidence_score = Column(Float)
    suggested_action = Column(String)

    # For duplicates
    potential_duplicate_id = Column(Integer, ForeignKey('transactions.id'))

    # User decision
    resolved = Column(Boolean, default=False)
    user_action = Column(String)  # 'confirm', 'ignore', 'merge', 'split'
```

---

## Next Step: Let's Build the Data Dumper!

I'll now create:
1. **API endpoint** `/api/data-dump` to receive raw data
2. **Database model** for storing raw dumps
3. **Step-by-step guide** to create your first shortcut
4. **Analysis script** to help you understand patterns

Ready to proceed?
