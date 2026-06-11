# HisaabAI — Complete Cursor Project Prompt + App Flow

---

# PART 1: CURSOR PROJECT PROMPT
> Copy everything below the divider and paste it into Cursor as your project instructions.

---

---

## PROJECT OVERVIEW

You are building **HisaabAI** — a WhatsApp-first AI business and money assistant for Pakistani small businesses, freelancers, and shopkeepers. The core UX is: the user never feels like they are using software. It feels like texting a smart accountant (munshi) on WhatsApp who understands Urdu, Roman Urdu, and English mixed messages.

This is a full-stack production application. Build it clean, modular, and production-ready from Day 1.

---

## WHAT THIS PRODUCT DOES

HisaabAI connects to WhatsApp via Meta's official Cloud API. When a user messages the WhatsApp number:

1. The message is received by a FastAPI webhook
2. AI extracts the intent and transaction data (even from voice notes or receipt images)
3. Data is stored in Supabase (Postgres)
4. The bot replies with a confirmation or asks a follow-up question
5. Users can generate invoices (PDF), Excel reports, view udhaar (credit) ledger, and get AI-powered business insights
6. A Next.js web dashboard shows full analytics, transaction history, and report downloads

**Primary interface:** WhatsApp
**Secondary interface:** Next.js web dashboard

---

## CORE FEATURES TO BUILD

### 1. WhatsApp Conversation Engine
- Receive any message type: text, voice note, image (receipt photo)
- Understand natural Urdu / Roman Urdu / English mixed input
- Maintain conversation state per user (multi-turn flows)
- Menu-based fallback for unrecognized messages

### 2. Transaction Management
- Record sales, expenses, and purchases from natural language
- Auto-categorize transactions (inventory, utilities, rent, salary, etc.)
- Support multiple businesses per user
- Full CRUD: view, edit, delete transactions

### 3. Udhaar (Credit) Tracking
- Record credit given to customers
- Record credit received from suppliers
- Track payment status and partial payments
- Automated WhatsApp reminders for overdue udhaar

### 4. Invoice Generation
- Generate professional PDF invoices with business logo placeholder
- Support: Cash, Bank Transfer, Easypaisa, JazzCash, Udhaar payment types
- Auto-number invoices (INV-001, INV-002...)
- Send invoice PDF directly back on WhatsApp

### 5. Excel Report Generation
- Monthly workbook with sheets: Sales, Expenses, Udhaar, Customers, Profit Summary
- User says "Excel bhejo" → receives .xlsx file on WhatsApp
- Auto-generated every month via n8n automation

### 6. AI-Powered Insights
- Weekly business insights via WhatsApp message
- Cash flow forecast (next 14 days based on patterns)
- Customer payment behavior analysis
- Expense trend detection
- Udhaar risk scoring (who is likely to default)

### 7. Voice Note Processing
- User sends Urdu/Roman Urdu voice note
- Whisper transcribes it
- LLM extracts transactions from transcription
- Confirmation sent back to user

### 8. Receipt/Bill OCR
- User sends photo of receipt or supplier bill
- EasyOCR extracts: items, amounts, vendor name, date
- AI structures into transaction record
- User confirms before saving

### 9. Web Dashboard (Next.js)
- Login via phone number + OTP (Supabase Auth)
- Dashboard: revenue chart, expenses chart, udhaar balance, profit this month
- Transaction history with filters
- Udhaar ledger per customer
- Invoice history with download links
- Business settings (name, category, logo upload)

### 10. Multi-Business Mode
- One WhatsApp number can manage multiple businesses
- User switches between businesses via command
- Separate records per business

---

## BUSINESS MODES

Support 4 business modes with slightly different workflows:

### Mode 1: Dukaan/Business
- Sales, expenses, inventory expenses, supplier udhaar, customer udhaar
- Invoice generation with tax (optional)

### Mode 2: Freelancing
- Project invoices (client name, project, amount, currency)
- Foreign payment tracking (USD, AED, GBP → PKR conversion note)
- SBP purpose code reminders on invoices

### Mode 3: Ghar ka Kharcha (Household)
- Monthly budget tracking
- Category expenses (groceries, school, electricity, rent)
- Budget vs actual comparison

### Mode 4: Farming/Kheti
- Crop expense tracking (seed, fertilizer, irrigation, labor)
- Harvest revenue recording
- Season-wise profit/loss

---

## TECH STACK

### Backend
```
Language:        Python 3.11+
Framework:       FastAPI
Task Queue:      Celery + Redis (Upstash free tier) for async tasks
Database ORM:    SQLAlchemy + Supabase Postgres
Auth:            Supabase Auth (phone OTP)
```

### AI / ML
```
LLM:             Groq API (primary - llama-3.1-70b-versatile, free tier)
Local LLM:       Ollama + llama3.1 (development fallback)
Agents:          LangGraph (multi-agent orchestration)
Embeddings:      sentence-transformers (all-MiniLM-L6-v2, free, local)
Vector DB:       Qdrant (Docker local dev, Qdrant Cloud free tier production)
Voice:           Whisper (openai-whisper library, open source, runs locally)
OCR:             EasyOCR (open source, runs locally)
```

### Document Generation
```
PDF Invoices:    ReportLab
Excel Reports:   openpyxl
```

### Frontend (Web Dashboard)
```
Framework:       Next.js 15 (App Router)
Styling:         Tailwind CSS
Components:      Shadcn/UI
Charts:          Recharts
State:           Zustand
Auth:            Supabase Auth + Next.js middleware
HTTP:            Axios
```

### Messaging
```
WhatsApp:        Meta WhatsApp Cloud API (official, free 1K conversations/month)
Webhook:         FastAPI endpoint (/webhook/whatsapp)
Email:           Resend (free 3K emails/month) - optional
```

### Automation
```
Scheduler:       n8n (self-hosted via Docker)
Jobs:            Weekly insights, monthly Excel reports, udhaar reminders
```

### Infrastructure
```
Frontend:        Vercel (free tier)
Backend:         Railway (free tier → $5/month when needed)
Database:        Supabase (free tier)
Vector DB:       Qdrant Cloud (free 1GB tier)
Cache/Queue:     Upstash Redis (free tier)
LLM:             Groq API (free tier)
WhatsApp:        Meta Cloud API (free)
Dev:             Docker Compose for local services
```

---

## COMPLETE FILE/FOLDER STRUCTURE

```
hisaab-ai/
│
├── backend/                          # FastAPI application
│   ├── main.py                       # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── webhook.py                # WhatsApp webhook endpoint
│   │   ├── dashboard.py              # REST API for Next.js dashboard
│   │   ├── auth.py                   # Auth endpoints
│   │   └── health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # Settings via pydantic-settings
│   │   ├── database.py               # SQLAlchemy + Supabase connection
│   │   └── security.py               # JWT utilities
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                   # User, Business
│   │   ├── transaction.py            # Sale, Expense, Purchase
│   │   ├── udhaar.py                 # UdhaarRecord, UdhaarPayment
│   │   ├── invoice.py                # Invoice, InvoiceItem
│   │   └── conversation.py          # ConversationState, MessageLog
│   │
│   ├── schemas/                      # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── udhaar.py
│   │   ├── invoice.py
│   │   └── whatsapp.py               # WhatsApp webhook payload schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── whatsapp.py               # WhatsApp API client (send messages, media)
│   │   ├── transaction_service.py    # Business logic for transactions
│   │   ├── udhaar_service.py         # Udhaar business logic
│   │   ├── invoice_service.py        # Invoice CRUD + PDF trigger
│   │   ├── report_service.py         # Excel report generation
│   │   └── insight_service.py        # AI insights generation
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── conversation_handler.py   # Main entry: routes message to correct agent
│   │   ├── intent_classifier.py      # Classify: sale/expense/invoice/report/udhaar/query
│   │   ├── transaction_extractor.py  # LLM extracts structured data from free text
│   │   ├── voice_processor.py        # Whisper transcription
│   │   ├── ocr_processor.py          # EasyOCR receipt processing
│   │   ├── memory.py                 # Qdrant vector memory for user's business
│   │   │
│   │   └── agents/                   # LangGraph agents (Phase 6)
│   │       ├── __init__.py
│   │       ├── graph.py              # LangGraph StateGraph definition
│   │       ├── supervisor.py         # Routes to correct sub-agent
│   │       ├── transaction_agent.py
│   │       ├── invoice_agent.py
│   │       ├── udhaar_agent.py
│   │       ├── insight_agent.py
│   │       ├── forecast_agent.py
│   │       └── tax_agent.py
│   │
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── pdf_invoice.py            # ReportLab PDF invoice generator
│   │   └── excel_report.py           # openpyxl Excel workbook generator
│   │
│   └── utils/
│       ├── __init__.py
│       ├── urdu_utils.py             # Roman Urdu normalization helpers
│       ├── currency.py               # PKR formatting utilities
│       └── date_utils.py
│
├── frontend/                         # Next.js 15 web dashboard
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # Landing / login
│   │   ├── (auth)/
│   │   │   └── login/page.tsx        # Phone OTP login
│   │   └── (dashboard)/
│   │       ├── layout.tsx            # Sidebar layout
│   │       ├── dashboard/page.tsx    # Main overview
│   │       ├── transactions/page.tsx
│   │       ├── udhaar/page.tsx
│   │       ├── invoices/page.tsx
│   │       ├── reports/page.tsx
│   │       └── settings/page.tsx
│   │
│   ├── components/
│   │   ├── ui/                       # Shadcn components
│   │   ├── dashboard/
│   │   │   ├── StatsCards.tsx        # Revenue, Expenses, Profit, Udhaar cards
│   │   │   ├── RevenueChart.tsx      # Monthly revenue line chart
│   │   │   ├── ExpenseBreakdown.tsx  # Pie chart by category
│   │   │   └── UdhaarSummary.tsx     # Top udhaar owed
│   │   ├── transactions/
│   │   │   └── TransactionTable.tsx
│   │   ├── udhaar/
│   │   │   └── UdhaarLedger.tsx
│   │   └── invoices/
│   │       └── InvoiceList.tsx
│   │
│   ├── lib/
│   │   ├── supabase.ts               # Supabase client
│   │   └── api.ts                    # Axios API client
│   │
│   └── types/
│       └── index.ts
│
├── docker-compose.yml                # Local dev: Qdrant, Redis, n8n, Ollama
├── docker-compose.prod.yml
└── README.md
```

---

## DATABASE SCHEMA

Build the following tables in Supabase (Postgres):

```sql
-- Users and Businesses
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE NOT NULL,   -- WhatsApp number with country code
    name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    active_business_id UUID,
    onboarding_complete BOOLEAN DEFAULT FALSE
);

CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50),               -- grocery, electronics, clothing, restaurant, freelance, household, farming, other
    mode VARCHAR(20) DEFAULT 'business', -- business, freelancing, household, farming
    phone VARCHAR(20),
    address TEXT,
    logo_url TEXT,
    currency VARCHAR(3) DEFAULT 'PKR',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,          -- sale, expense, purchase
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT,
    category VARCHAR(100),              -- inventory, utilities, rent, salary, food, transport, etc.
    customer_name VARCHAR(200),
    vendor_name VARCHAR(200),
    payment_method VARCHAR(50),         -- cash, bank_transfer, easypaisa, jazzcash, udhaar, online
    reference_number VARCHAR(100),
    notes TEXT,
    transaction_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(20) DEFAULT 'whatsapp' -- whatsapp, dashboard, voice, ocr
);

-- Udhaar (Credit) System
CREATE TABLE udhaar_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    party_name VARCHAR(200) NOT NULL,
    party_phone VARCHAR(20),
    party_type VARCHAR(10) NOT NULL,    -- customer (gave udhaar) or supplier (received udhaar)
    total_amount DECIMAL(12, 2) NOT NULL,
    paid_amount DECIMAL(12, 2) DEFAULT 0,
    due_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, partial, paid
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_reminder_sent TIMESTAMPTZ
);

CREATE TABLE udhaar_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    udhaar_id UUID REFERENCES udhaar_records(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date DATE DEFAULT CURRENT_DATE,
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_phone VARCHAR(20),
    subtotal DECIMAL(12, 2) NOT NULL,
    discount DECIMAL(12, 2) DEFAULT 0,
    tax_amount DECIMAL(12, 2) DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid, paid, udhaar
    due_date DATE,
    pdf_url TEXT,                       -- Supabase Storage URL
    notes TEXT,
    invoice_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    item_name VARCHAR(300) NOT NULL,
    quantity DECIMAL(10, 2) DEFAULT 1,
    unit_price DECIMAL(12, 2) NOT NULL,
    total_price DECIMAL(12, 2) NOT NULL
);

-- Conversation State (for multi-turn WhatsApp flows)
CREATE TABLE conversation_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_phone VARCHAR(20) UNIQUE NOT NULL,
    state VARCHAR(100),                 -- current flow state: awaiting_customer_name, awaiting_payment_method, etc.
    context JSONB DEFAULT '{}',         -- temporary data collected in multi-turn flow
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE message_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_phone VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,     -- inbound, outbound
    message_type VARCHAR(20),           -- text, image, audio, document
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## ENVIRONMENT VARIABLES

```bash
# .env (backend)

# WhatsApp
WHATSAPP_TOKEN=your_meta_whatsapp_token
WHATSAPP_PHONE_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_verify_string
WHATSAPP_API_VERSION=v19.0

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# AI
GROQ_API_KEY=your_groq_api_key
OLLAMA_BASE_URL=http://localhost:11434   # local dev only

# Vector DB
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_cloud_key    # production only

# Redis
UPSTASH_REDIS_URL=redis://...
UPSTASH_REDIS_TOKEN=...

# Storage
SUPABASE_STORAGE_BUCKET=hisaab-files

# App
SECRET_KEY=your_jwt_secret
ENVIRONMENT=development                 # development | production
APP_URL=https://your-backend.railway.app
```

---

## WHATSAPP WEBHOOK IMPLEMENTATION

The webhook is the heart of the application. Build it exactly as follows:

```python
# backend/api/webhook.py

@router.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    """Meta WhatsApp webhook verification"""
    if hub_mode == "subscribe" and hub_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403)


@router.post("/webhook/whatsapp")
async def receive_message(payload: WhatsAppWebhookPayload, background_tasks: BackgroundTasks):
    """Receive and process WhatsApp messages"""
    # Extract message from payload
    # Handle: text, audio (voice note), image (receipt)
    # Mark message as read immediately
    # Process in background (avoid WhatsApp timeout)
    background_tasks.add_task(process_whatsapp_message, payload)
    return {"status": "ok"}
```

---

## AI CONVERSATION HANDLER

This is the brain. Build it as a pipeline:

```python
# backend/ai/conversation_handler.py

async def handle_message(user_phone: str, message: dict) -> str:
    """
    Main message processing pipeline:
    1. Get or create user + active business
    2. Get current conversation state
    3. If in a flow (awaiting input), continue that flow
    4. If new message, classify intent
    5. Route to appropriate handler
    6. Update conversation state
    7. Return response text
    """
    
    # Message types to handle:
    # - text: classify intent → route
    # - audio: transcribe with Whisper → treat as text
    # - image: run OCR → extract transaction data
```

### Intent Classification

The LLM should classify each message into one of:
```
sale          → "1000 ki sale hui", "500 mila", "TV becha 45000 mein"
expense       → "1200 ka maal khareeda", "bijli ka bill 3000"
invoice       → "invoice banao", "bill chahiye"
udhaar_give   → "Ahmed ko 5000 udhaar diya"
udhaar_receive → "supplier ne 10000 ka maal diya udhaar par"
udhaar_pay    → "Ahmed ne 2000 de diye"
report        → "report do", "is month kitna hua", "summary"
excel         → "excel bhejo", "sheet chahiye"
insights      → "kya trend chal raha hai", "business kaisa chal raha"
help          → "kya kar sakte ho", "menu"
unknown       → anything unclear → show main menu
```

---

## TRANSACTION EXTRACTION PROMPT

```python
EXTRACTION_PROMPT = """
You are a financial data extraction assistant for Pakistani small businesses.
Extract transaction information from the following message.

The message may be in:
- Urdu (اردو)
- Roman Urdu (Urdu written in English letters)
- English
- A mix of all three

Message: {message}

Extract and return ONLY a JSON object with these fields:
{{
  "transaction_type": "sale" | "expense" | "purchase",
  "amount": <number in PKR, null if not found>,
  "description": "<what was sold/bought, in English>",
  "customer_or_vendor": "<name if mentioned, null if not>",
  "category": "<best guess category: inventory|utilities|rent|salary|food|transport|other>",
  "payment_method": "cash|bank_transfer|easypaisa|jazzcash|udhaar|unknown",
  "quantity": <number or null>,
  "confidence": <0.0 to 1.0>
}}

If amount cannot be determined, set amount to null.
Return ONLY the JSON. No explanation.
"""
```

---

## WHATSAPP RESPONSE MESSAGES

Define all response templates. Keep them in Urdu/Roman Urdu with emojis:

```python
# backend/utils/messages.py

MESSAGES = {
    "welcome": """Assalamualaikum! 👋

Main *HisaabAI* hoon — aapka digital munshi.

Main aapki madad kar sakta hoon:
✅ Sale aur expenses record karna
✅ Invoice banana
✅ Udhaar track karna
✅ Monthly reports banana
✅ Business insights dena

Sab kuch WhatsApp par! 🎉

Shuru karte hain — aapka business ka naam kya hai?""",

    "setup_category": """Business category select karein:

1️⃣ Grocery / General Store
2️⃣ Electronics
3️⃣ Clothing / Kapra
4️⃣ Restaurant / Dhaba
5️⃣ Pharmacy / Medical
6️⃣ Freelancing
7️⃣ Ghar ka Kharcha
8️⃣ Farming / Kheti
9️⃣ Other""",

    "main_menu": """*{business_name}* 📊

Kya karna chahte hain?

1️⃣ Sale add karo
2️⃣ Expense add karo
3️⃣ Invoice banao
4️⃣ Udhaar track karo
5️⃣ Report dekho
6️⃣ Excel report
7️⃣ Insights dekho
8️⃣ Help""",

    "sale_recorded": """✅ *Sale Record Ho Gayi!*

💰 Amount: Rs. {amount:,}
📝 Item: {description}
💳 Payment: {payment_method}
📅 Date: {date}

Is mahine ki total sale: *Rs. {monthly_total:,}*

Aur kuch add karna hai?""",

    "expense_recorded": """✅ *Expense Record Ho Gaya!*

💸 Amount: Rs. {amount:,}
📝 Description: {description}
🏷️ Category: {category}
📅 Date: {date}

Is mahine ke kharche: *Rs. {monthly_expenses:,}*""",

    "invoice_ask_customer": """Invoice banana hai! ✅

Customer ka naam kya hai?""",

    "invoice_ask_payment": """Payment method kya hai?

1️⃣ Cash
2️⃣ Bank Transfer
3️⃣ Easypaisa
4️⃣ JazzCash
5️⃣ Udhaar (baad mein milega)""",

    "invoice_ready": """✅ *Invoice Ready Hai!*

🧾 Invoice #: {invoice_number}
👤 Customer: {customer_name}
💰 Total: Rs. {total:,}
💳 Payment: {payment_method}

PDF file aapko abhi bhej raha hoon... 📄""",

    "udhaar_recorded": """✅ *Udhaar Record Ho Gaya!*

👤 Party: {party_name}
💰 Amount: Rs. {amount:,}
📅 Due Date: {due_date}

Reminder automatically {due_date} se pehle bhej diya jayega. ⏰""",

    "monthly_report": """📊 *{month} {year} Summary*
━━━━━━━━━━━━━━━━━━━
💰 Total Sale: Rs. {revenue:,}
💸 Total Kharcha: Rs. {expenses:,}
📈 *Net Profit: Rs. {profit:,}*
━━━━━━━━━━━━━━━━━━━
🏆 Best Sale Day: {best_day}
⚠️ Outstanding Udhaar: Rs. {udhaar_total:,}
━━━━━━━━━━━━━━━━━━━

Excel report chahiye? "Excel bhejo" likhein.""",

    "weekly_insights": """📈 *Weekly Business Insights*
━━━━━━━━━━━━━━━━━━━
{insight_1}
{insight_2}
{insight_3}
━━━━━━━━━━━━━━━━━━━
💡 Tip: {tip}""",

    "udhaar_reminder": """⏰ *Payment Reminder*

Assalamualaikum {party_name},

{business_name} ki taraf se reminder:
💰 Aapka Rs. {amount:,} baaki hai
📅 Due Date: {due_date}

Please payment kar dein. Shukriya! 🙏""",

    "voice_transcribed": """🎙️ Aapki awaaz sun li:

_"{transcription}"_

Kya yeh sahi hai?
1️⃣ Haan, save karo
2️⃣ Nahi, dobara likho""",

    "receipt_scanned": """📸 Receipt scan ho gayi!

Yeh items mili hain:
{items_list}

Total: Rs. {total:,}

Kya yeh sahi hai?
1️⃣ Haan, save karo
2️⃣ Nahi, change karo""",
    
    "unknown": """Mujhe samajh nahi aaya. 🤔

Main menu ke liye *menu* likhein.""",

    "error": """Kuch masla ho gaya. 😔 Dobara try karein ya *menu* likhein."""
}
```

---

## PDF INVOICE DESIGN

Build a clean, professional invoice using ReportLab:

```python
# backend/generators/pdf_invoice.py
# Invoice should include:
# - Business name + logo placeholder (top left)
# - "INVOICE" heading (top right)  
# - Invoice number, date (top right)
# - Business address/phone (below logo)
# - Customer details section
# - Items table: Item Name | Qty | Unit Price | Total
# - Subtotal, Discount (if any), Tax (if any), TOTAL (bold)
# - Payment method + status
# - Footer: "Generated by HisaabAI" + business phone
# Colors: Professional (dark blue header, clean white body)
# Font: Use built-in ReportLab fonts (no external font dependencies)
```

---

## EXCEL REPORT STRUCTURE

```python
# backend/generators/excel_report.py
# Monthly workbook with these sheets:

# Sheet 1: Summary
# - Month/Year header
# - Total Revenue, Total Expenses, Net Profit
# - Udhaar outstanding (given + received)

# Sheet 2: Sales
# Columns: Date | Description | Customer | Payment Method | Amount

# Sheet 3: Expenses  
# Columns: Date | Description | Category | Payment Method | Amount

# Sheet 4: Udhaar Given (to customers)
# Columns: Customer Name | Phone | Amount | Paid | Balance | Due Date | Status

# Sheet 5: Udhaar Received (from suppliers)
# Columns: Supplier Name | Phone | Amount | Paid | Balance | Due Date | Status

# Sheet 6: Invoices
# Columns: Invoice # | Date | Customer | Items | Total | Payment | Status

# Styling: 
# - Header row: dark blue background, white bold text
# - Alternate row colors: white / light gray
# - Currency columns: formatted as #,##0.00
# - Total rows: bold
```

---

## LANGGRAPH AGENT ARCHITECTURE

Build this in Phase 6 (after core flows work):

```python
# backend/ai/agents/graph.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class HisaabState(TypedDict):
    user_phone: str
    business_id: str
    raw_message: str
    message_type: str          # text, audio, image
    intent: str                # classified intent
    extracted_data: dict       # structured data from LLM
    agent_result: dict         # what the agent produced
    response_text: str         # final WhatsApp response
    files_to_send: list        # PDFs/Excel to send
    requires_confirmation: bool
    error: str | None

# Nodes:
# 1. classify_intent      → determines which agent to use
# 2. transaction_agent    → handles sale/expense/purchase
# 3. invoice_agent        → creates invoice PDF
# 4. udhaar_agent         → manages credit records
# 5. insight_agent        → generates AI insights
# 6. forecast_agent       → cash flow prediction
# 7. report_agent         → Excel/summary reports
# 8. tax_agent            → FBR-related queries
# 9. send_response        → final node: sends WhatsApp message

# Edges:
# classify_intent → [transaction|invoice|udhaar|insight|forecast|report|tax] based on intent
# all agents → send_response → END
```

---

## VOICE NOTE PROCESSING

```python
# backend/ai/voice_processor.py
import whisper

# Load model once at startup
# Use "small" model for speed, "medium" for better Urdu accuracy
# The "small" model is ~140MB and handles Urdu reasonably well
# "medium" is ~460MB and significantly better for Urdu

async def transcribe_voice(audio_url: str) -> str:
    """
    1. Download audio file from WhatsApp CDN using WHATSAPP_TOKEN
    2. Convert to wav if needed (WhatsApp sends OGG/OPUS)
    3. Run Whisper transcription with language="ur" hint
    4. Return transcribed text
    """
```

---

## RECEIPT OCR PROCESSING

```python
# backend/ai/ocr_processor.py
import easyocr

# Initialize reader with Urdu + English
reader = easyocr.Reader(['ur', 'en'])

async def extract_from_receipt(image_url: str) -> dict:
    """
    1. Download image from WhatsApp CDN
    2. Run EasyOCR
    3. Pass extracted text to LLM for structuring:
       - Find: vendor name, date, items, amounts, total
    4. Return structured dict
    """
```

---

## N8N AUTOMATION WORKFLOWS

Set up these automated workflows in n8n:

### Workflow 1: Daily Udhaar Reminders
```
Trigger: Every day at 9 AM PKT
Query Supabase: Find udhaar_records where due_date = tomorrow AND status != 'paid'
For each: Send WhatsApp reminder to business owner
For each (if party_phone exists): Send reminder to customer/supplier
```

### Workflow 2: Weekly Business Insights
```
Trigger: Every Monday at 10 AM PKT
For each active business:
  - Calculate last 7 days transactions
  - Call /api/insights/{business_id} endpoint
  - Send insights message via WhatsApp
```

### Workflow 3: Monthly Excel Report
```
Trigger: 1st of every month at 8 AM PKT
For each active business with transactions last month:
  - Call /api/reports/excel/{business_id}?month=last_month
  - Send Excel file via WhatsApp
  - "Aapki {month} ki Excel report ready hai! 📊"
```

### Workflow 4: Cash Flow Warning
```
Trigger: Every Sunday at 6 PM PKT
For each business:
  - Analyze last 30 days expense rate
  - If projected to go negative in 14 days: send warning
```

---

## NEXT.JS DASHBOARD PAGES

### Dashboard Page (`/dashboard`)
```
Stats Cards (top row):
- This Month Revenue: Rs. X,XXX (green, up/down % vs last month)
- This Month Expenses: Rs. X,XXX (red)
- Net Profit: Rs. X,XXX (green/red)
- Udhaar Outstanding: Rs. X,XXX (orange)

Charts:
- Revenue vs Expenses: Line chart, last 6 months
- Expense Breakdown: Pie chart by category

Tables:
- Recent Transactions: last 10, with type badge
- Top Udhaar: top 5 people who owe money
```

### Transactions Page (`/transactions`)
```
- Filter: date range, type (sale/expense/purchase), payment method
- Search by description or customer name
- Table: Date | Type | Description | Amount | Payment | Source (WhatsApp/Voice/OCR)
- Export to Excel button
```

### Udhaar Page (`/udhaar`)
```
- Tab 1: Given (to customers) — Amount, Paid, Balance, Due Date, Status, Actions
- Tab 2: Received (from suppliers)
- Click a party: see full payment history
- "Send Reminder" button per record
- "Record Payment" button
```

### Invoices Page (`/invoices`)
```
- List of all invoices with status badge
- Click: full invoice view
- Download PDF button
- "Send to Customer" button (resends on WhatsApp)
```

---

## SECURITY REQUIREMENTS

1. Webhook endpoint must verify Meta's `X-Hub-Signature-256` header
2. All dashboard API endpoints require Supabase Auth JWT
3. Row-Level Security (RLS) on all Supabase tables — users can only see their own data
4. Rate limiting on webhook: 100 requests/minute per phone number
5. Validate all phone numbers are in E.164 format (+92XXXXXXXXXX)
6. Sanitize all user input before LLM prompts (prevent prompt injection)
7. Store all files in Supabase Storage with signed URLs (not public)

---

## PHASE BUILD ORDER

Build in this exact sequence. Do NOT skip ahead:

### Phase 1 (Week 1–3): Core Plumbing
- [ ] FastAPI project setup with folder structure
- [ ] Supabase database setup + all tables
- [ ] WhatsApp webhook (verify + receive)
- [ ] Basic text response (echo back message)
- [ ] User creation on first message
- [ ] Onboarding flow (business name → category → phone)
- [ ] Menu-based navigation (numbered options)
- [ ] Manual transaction recording via menu

### Phase 2 (Week 4–5): Document Generation
- [ ] PDF invoice generator (ReportLab)
- [ ] Invoice flow via WhatsApp (multi-turn)
- [ ] Excel monthly report (openpyxl)
- [ ] File sending via WhatsApp API
- [ ] Supabase Storage for generated files

### Phase 3 (Week 6–7): AI Transaction Understanding
- [ ] Groq API integration
- [ ] Intent classifier (LLM-based)
- [ ] Transaction extractor with structured output
- [ ] Natural language transaction recording
- [ ] Udhaar recording from natural language

### Phase 4 (Week 8–9): Voice + OCR
- [ ] Whisper integration for voice notes
- [ ] EasyOCR for receipt photos
- [ ] Confirmation flow before saving OCR results

### Phase 5 (Week 10–12): AI Memory + Insights
- [ ] Qdrant setup + embedding pipeline
- [ ] Transaction history embedding
- [ ] AI weekly insights generation
- [ ] Cash flow forecasting
- [ ] Customer payment behavior analysis

### Phase 6 (Week 13–16): LangGraph Agents
- [ ] SupervisorAgent
- [ ] TransactionAgent, InvoiceAgent, UdhaarAgent
- [ ] InsightAgent, ForecastAgent, TaxAgent
- [ ] Replace simple handler with LangGraph graph

### Phase 7 (Week 17–20): Web Dashboard + Launch
- [ ] Next.js dashboard (all pages)
- [ ] Supabase Auth with phone OTP
- [ ] n8n automation workflows
- [ ] Freelancer mode
- [ ] Farmer mode
- [ ] Stripe billing (Pakistani card support via Stripe)

---

## IMPORTANT IMPLEMENTATION NOTES

1. **Urdu handling**: Always use UTF-8 encoding. Test with actual Urdu text like "آج 5000 کی سیل ہوئی". Roman Urdu ("aaj 5000 ki sale hui") is more common — optimize for this first.

2. **WhatsApp message limits**: Messages over 4096 characters get cut off. Split long messages.

3. **Conversation state**: Store state in both Redis (for speed) and Supabase (for persistence). Redis TTL: 30 minutes. If Redis misses, fall back to Supabase.

4. **Async everything**: All WhatsApp processing must be async. Return 200 OK to Meta immediately, process in background.

5. **Error handling**: Every error must send a user-friendly Urdu message. Never let the bot go silent.

6. **Phone number format**: Always store as +92XXXXXXXXXX. Normalize on input.

7. **Currency**: Always store in PKR as DECIMAL(12,2). Format display as "Rs. X,XXX" (Pakistani convention, no decimal for round amounts).

8. **Whisper language**: Set `language="ur"` for better Urdu transcription. If confidence is low, try without language hint.

9. **Free tier limits**: Groq free tier = 6,000 requests/day. Cache LLM responses where possible. Meta free tier = 1,000 conversations/month (each unique user = 1 conversation/24hrs).

10. **Testing**: Create a test WhatsApp number using Meta's test mode. Build a `/test` endpoint that simulates WhatsApp messages for development without using real API calls.

---

## DOCKER COMPOSE (LOCAL DEV)

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=hisaab123
    volumes:
      - n8n_data:/home/node/.n8n

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  qdrant_data:
  n8n_data:
  ollama_data:
```

---

---

# PART 2: COMPLETE APP FLOW
> What the user actually experiences — every WhatsApp interaction from start to finish.

---

## FLOW 1: FIRST TIME USER (ONBOARDING)

```
USER sends any message (or scans QR code)
  ↓
BOT: "Assalamualaikum! 👋 Main HisaabAI hoon..."
     [Shows full welcome message with 4 modes]

USER: "1" (Dukaan/Business)
  ↓
BOT: "Business ka naam kya hai?"

USER: "Khan Electronics"
  ↓
BOT: "Category select karein: 1-Grocery 2-Electronics..."

USER: "2"
  ↓
BOT: "Invoice par kaunsa phone number show karna hai?"

USER: "03001234567"
  ↓
BOT: "✅ Setup complete! Khan Electronics ready hai. 
      Aaj kya karna chahte hain? [main menu]"

→ User is created in DB. Business is created. Active business set.
```

---

## FLOW 2: RECORDING A SALE (NATURAL LANGUAGE)

```
USER: "aaj LED TV becha 45000 mein Ahmed ko"
  ↓
[AI classifies: SALE]
[AI extracts: amount=45000, description="LED TV", customer="Ahmed"]
  ↓
BOT: "✅ Sale Record Ho Gayi!
      💰 Amount: Rs. 45,000
      📝 Item: LED TV
      👤 Customer: Ahmed
      💳 Payment: Cash (assumed)
      
      Sahi hai? 1-Haan  2-Change karo"

USER: "1"
  ↓
[Transaction saved to Supabase]
  ↓
BOT: "✅ Saved! Is mahine ki total sale: Rs. 1,23,000"
```

---

## FLOW 3: RECORDING A SALE (AMBIGUOUS)

```
USER: "500 aye"
  ↓
[AI classifies: SALE — low confidence, amount=500]
  ↓
BOT: "500 rupaye ki sale record karoon?
      Kya becha? (ya 'skip' likhein)"

USER: "chai aur biscuits"
  ↓
BOT: "✅ Sale Record Ho Gayi!
      💰 Rs. 500 — Chai aur biscuits
      
      Is mahine ki total: Rs. 45,500"
```

---

## FLOW 4: RECORDING AN EXPENSE

```
USER: "bijli ka bill 3200 diya"
  ↓
[AI classifies: EXPENSE]
[AI extracts: amount=3200, description="Bijli ka bill", category="utilities"]
  ↓
BOT: "✅ Expense Record Ho Gaya!
      💸 Rs. 3,200 — Bijli ka bill
      🏷️ Category: Utilities
      
      Is mahine ke total kharche: Rs. 18,500"
```

---

## FLOW 5: INVOICE GENERATION

```
USER: "invoice banao:
       LED TV - 45,000
       HDMI Cable - 2,000  
       Installation - 5,000"
  ↓
[AI classifies: INVOICE]
[AI extracts items with amounts]
  ↓
BOT: "Invoice banana hai! ✅
      
      Items:
      • LED TV — Rs. 45,000
      • HDMI Cable — Rs. 2,000
      • Installation — Rs. 5,000
      Total: Rs. 52,000
      
      Customer ka naam?"

USER: "Ali Traders"
  ↓
BOT: "Payment method?
      1-Cash 2-Bank 3-Easypaisa 4-JazzCash 5-Udhaar"

USER: "1"
  ↓
[PDF generated with ReportLab]
[PDF uploaded to Supabase Storage]
[PDF sent as WhatsApp document]
  ↓
BOT: "✅ Invoice #INV-007 Ready!
      👤 Ali Traders
      💰 Rs. 52,000
      💳 Cash"
[PDF document delivered on WhatsApp]
```

---

## FLOW 6: UDHAAR (CREDIT) TRACKING

```
USER: "Ahmed ko 15000 udhaar diya"
  ↓
[AI classifies: UDHAAR_GIVE]
[AI extracts: party_name="Ahmed", amount=15000]
  ↓
BOT: "Due date kya hai? (date likhein ya 'skip')"

USER: "15 July"
  ↓
[Udhaar record created in Supabase]
  ↓
BOT: "✅ Udhaar Record Ho Gaya!
      👤 Ahmed
      💰 Rs. 15,000
      📅 Due: 15 July 2025
      
      Reminder 14 July ko automatically bheja jayega. ⏰
      
      Total outstanding udhaar: Rs. 47,000"

--- Later, Ahmed pays ---

USER: "Ahmed ne 10000 de diye"
  ↓
[AI classifies: UDHAAR_PAYMENT]
[Matches to Ahmed's existing record]
  ↓
BOT: "✅ Payment Record Ho Gaya!
      👤 Ahmed
      💰 Mila: Rs. 10,000
      ⚠️ Baaki: Rs. 5,000
      
      Ahmed ka balance: Rs. 5,000 (due 15 July)"
```

---

## FLOW 7: MONTHLY REPORT

```
USER: "is month ki report do"
  ↓
[Queries Supabase for current month transactions]
  ↓
BOT: "📊 June 2025 Summary
      ━━━━━━━━━━━━━━━━━
      💰 Total Sale: Rs. 4,85,000
      💸 Total Kharcha: Rs. 3,20,000
      📈 Net Profit: Rs. 1,65,000
      ━━━━━━━━━━━━━━━━━
      🏆 Best Sale Day: Friday
      ⚠️ Outstanding Udhaar: Rs. 74,000
      ━━━━━━━━━━━━━━━━━
      
      Excel report ke liye 'excel bhejo' likhein 📊"
```

---

## FLOW 8: EXCEL REPORT

```
USER: "excel bhejo"
  ↓
[openpyxl generates monthly workbook]
[6 sheets: Summary, Sales, Expenses, Udhaar Given, Udhaar Received, Invoices]
[File uploaded to Supabase Storage]
[Excel file sent as WhatsApp document]
  ↓
BOT: "✅ June_2025_Khan_Electronics.xlsx ready hai!"
[.xlsx file delivered on WhatsApp]

User opens it on phone/laptop — fully formatted professional spreadsheet.
```

---

## FLOW 9: VOICE NOTE INPUT

```
USER sends 🎙️ voice note: 
  "Aaj ek customer aaya tha, usne 3 fans khareede 
   2700 ke hisaab se, total 8100 hue. Cash diya.
   Aur maal ki delivery ka kharcha 500 tha."
  ↓
[Whisper transcribes the audio]
  ↓
BOT: "🎙️ Aapki awaaz sun li:
      
      _'Aaj ek customer aaya tha, usne 3 fans khareede...'_
      
      Yeh transactions mili hain:
      1. Sale: 3x Fan @ Rs. 2,700 = Rs. 8,100 (Cash)
      2. Expense: Delivery = Rs. 500
      
      Dono save karoon?
      1-Haan  2-Sirf sale  3-Nahi"

USER: "1"
  ↓
[Both transactions saved]
  ↓
BOT: "✅ Dono record ho gayi!
      💰 Sale: Rs. 8,100
      💸 Expense: Rs. 500"
```

---

## FLOW 10: RECEIPT PHOTO (OCR)

```
USER sends 📸 photo of a supplier bill
  ↓
[EasyOCR extracts text from image]
[LLM structures the extracted text]
  ↓
BOT: "📸 Receipt scan ho gayi!
      
      Yeh items mili hain:
      • Samsung 43' LED TV × 2 — Rs. 78,000
      • HDMI Cable × 5 — Rs. 2,500
      • Vendor: Malik Electronics
      • Total: Rs. 80,500
      
      Purchase record karoon?
      1-Haan  2-Nahi  3-Edit karo"

USER: "1"
  ↓
[Purchase transaction saved + inventory expense recorded]
  ↓
BOT: "✅ Purchase Record Ho Gaya!
      💸 Rs. 80,500 — Malik Electronics
      🏷️ Category: Inventory"
```

---

## FLOW 11: AI INSIGHTS

```
USER: "mera business kaisa chal raha hai"
  ↓
[InsightAgent queries last 30 days data]
[RAG over embedded transaction history]
[LLM generates personalized insights]
  ↓
BOT: "📈 Khan Electronics — Business Insights
      ━━━━━━━━━━━━━━━━━
      
      📊 Is mahine ka profit last month se 12% zyada hai. 
         Wajah: TV sales mein izafa.
      
      ⚠️ 3 customers ka udhaar 30 din se zyada se pending 
         hai. Total: Rs. 45,000.
      
      💡 Friday aapka best sales day hai (24% weekly revenue). 
         Friday ko zyada stock ready rakhein.
      
      🔮 Agle 14 din mein cashflow normal rahega. 
         Koi immediate issue nahi.
      
      ━━━━━━━━━━━━━━━━━
      💡 Tip: Bijli ka bill har mahine 8th ko aata hai — 
         pehle se Rs. 3,000 alag rakhein."
```

---

## FLOW 12: UNKNOWN / CONFUSED INPUT

```
USER: "kya scene hai bhai"
  ↓
[AI cannot classify intent]
  ↓
BOT: "Mujhe samajh nahi aaya. 🤔
      
      Kya karna chahte hain?
      • Sale: 'aaj 5000 ki sale hui'
      • Expense: '2000 ka maal khareeda'
      • Invoice: 'invoice banao'
      • Udhaar: 'Ahmed ko 10k udhaar diya'
      • Report: 'is month ki report'
      • Excel: 'excel bhejo'
      
      Ya 'menu' likhein."
```

---

## FLOW 13: AUTOMATED UDHAAR REMINDER (n8n)
*This runs automatically — no user input needed*

```
[n8n fires at 9 AM, checks tomorrow's due dates]
  ↓
[Finds: Ahmed owes Khan Electronics Rs. 15,000, due tomorrow]
  ↓
BOT sends to BUSINESS OWNER:
  "⏰ Payment Reminder
   
   Kal due hai:
   👤 Ahmed — Rs. 15,000
   
   Ahmed ko reminder bheja gaya hai."

BOT sends to AHMED (if phone on file):
  "Assalamualaikum Ahmed bhai,
   
   Khan Electronics ki taraf se reminder:
   💰 Aapka Rs. 15,000 kal tak due hai.
   
   JazzCash/Easypaisa: 03001234567
   
   Shukriya! 🙏"
```

---

## FLOW 14: AUTOMATED WEEKLY INSIGHTS (n8n)
*Every Monday, automatically sent*

```
[n8n fires Monday 10 AM]
  ↓
[Calculates last 7 days stats]
  ↓
BOT sends to business owner:
  "📈 Weekly Insights — Khan Electronics
   
   ✅ Is hafte ki sale: Rs. 1,23,000
   💸 Kharche: Rs. 45,000
   📈 Profit: Rs. 78,000
   
   📊 Last week se 8% zyada sale
   ⚠️ 2 naye udhaar records pending
   🏆 Best day: Saturday
   
   Have a great week! 💪"
```

---

## WEB DASHBOARD FLOW

```
User visits hisaabai.pk
  ↓
Login: Enter phone number → receive OTP on WhatsApp → verify
  ↓
Dashboard loads:
┌─────────────────────────────────────────────┐
│ Khan Electronics          June 2025         │
│                                             │
│ [Rs. 4,85,000]  [Rs. 3,20,000]  [Rs. 1,65,000]  [Rs. 74,000] │
│  This Month Rev   Expenses       Net Profit   Udhaar Due   │
│                                             │
│ [Revenue vs Expenses Chart — 6 months]      │
│                                             │
│ [Expense Breakdown Pie]  [Top Udhaar List]  │
│                                             │
│ Recent Transactions:                        │
│ Today  Sale   LED TV      Rs. 45,000  Cash  │
│ Today  Exp    Bijli Bill  Rs. 3,200   Cash  │
│ ...                                         │
└─────────────────────────────────────────────┘
```

---

## SUMMARY: WHAT THE OUTPUT LOOKS LIKE

| User Action | What They Receive |
|---|---|
| Type a sale in any way | Instant confirmation + running monthly total |
| Say amount + items for invoice | Professional PDF invoice on WhatsApp in ~10 seconds |
| Say udhaar given | Record saved + automatic reminder scheduled |
| Send voice note about day's business | All transactions extracted, confirmed, saved |
| Send photo of supplier bill | Items OCR'd, structured, saved as purchase |
| Ask for monthly report | Full P&L summary as WhatsApp message |
| Say "excel bhejo" | Formatted .xlsx with 6 sheets, delivered on WhatsApp |
| Ask for insights | Personalized AI analysis of their business patterns |
| Do nothing (n8n fires) | Monday insights, udhaar reminders, monthly Excel auto-sent |
| Visit web dashboard | Full analytics, charts, transaction history, invoice downloads |

---

*HisaabAI — Aapka digital munshi, hamesha WhatsApp par.*
