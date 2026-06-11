# HisaabAI — Complete Build Guide

### From Zero to Working Product, Step by Step

*Written for Fareeha — assuming strong frontend skills, learning backend + AI*

---

## BEFORE YOU START: THE MENTAL MODEL

Think of this project like building a restaurant:

- **The kitchen** = your FastAPI backend (does all the work, nobody sees it)
- **The waiters** = your APIs (carry messages between kitchen and customer)
- **The customer's table** = WhatsApp (where user talks to the bot)
- **The dining room** = Next.js dashboard (where users see everything nicely)
- **The recipe book** = your AI / LangGraph agents (knows what to do)
- **The fridge** = Supabase database (stores everything)
- **The prep cook** = n8n (does boring repetitive jobs automatically)

You already know how to build the dining room (Next.js). This guide teaches you the kitchen, the waiters, and the recipe book.

---

## THE BIG PICTURE: HOW A MESSAGE FLOWS

When a user sends "5000 ki sale hui" on WhatsApp, here is EXACTLY what happens:

```
User's Phone
    ↓ (WhatsApp sends the message to Meta's servers)
Meta's Servers
    ↓ (Meta forwards it to YOUR server via webhook)
Your FastAPI Server  ← this is YOUR code running on Railway
    ↓ (receives the message as JSON)
Intent Classifier (AI)
    ↓ (figures out: this is a SALE)
Transaction Extractor (AI)
    ↓ (pulls out: amount=5000, type=sale)
Transaction Service
    ↓ (saves to database)
Supabase Database  ← stored permanently
    ↓ (confirmation back)
WhatsApp Service
    ↓ (calls Meta API to send reply)
User's Phone  ← "✅ Sale recorded! Rs. 5,000"
```

The whole thing happens in about 2-3 seconds.

---

## YOUR DEVELOPMENT ENVIRONMENT

### What You Need Installed on Your Laptop

```
1. Python 3.11+          — for backend
2. Node.js 18+           — for frontend
3. Docker Desktop        — runs Qdrant, Redis, n8n locally
4. Git                   — version control
5. VS Code or Cursor     — your editor
6. Postman               — test your APIs
7. ngrok                 — expose your local server to WhatsApp (for testing)
```

### Install Python 3.11

Go to python.org → download 3.11 → install.
Check: open terminal, type `python --version` → should say Python 3.11.x

### Install Docker Desktop

Go to docker.com → download Docker Desktop → install.
This is how you run Qdrant, Redis, and n8n locally without installing them.

### Install ngrok

Go to ngrok.com → sign up free → download → follow their setup guide.
ngrok gives your laptop a public URL like `https://abc123.ngrok.io` so WhatsApp can reach it.

---

## ACCOUNTS YOU NEED TO CREATE (ALL FREE)

Do this before writing a single line of code:


| Service            | What it does               | URL                     | Cost      |
| ------------------ | -------------------------- | ----------------------- | --------- |
| **Supabase**       | Your database + auth       | supabase.com            | Free      |
| **Groq**           | AI/LLM API (fast + free)   | console.groq.com        | Free      |
| **Meta Developer** | WhatsApp API access        | developers.facebook.com | Free      |
| **Railway**        | Host your FastAPI backend  | railway.app             | Free / $5 |
| **Vercel**         | Host your Next.js frontend | vercel.com              | Free      |
| **Qdrant Cloud**   | Vector database            | cloud.qdrant.io         | Free 1GB  |
| **Upstash**        | Redis (for caching)        | upstash.com             | Free      |
| **Resend**         | Email sending              | resend.com              | Free      |
| **GitHub**         | Store your code            | github.com              | Free      |


Create all of these now. Save all API keys in a safe document.

---

## PROJECT FOLDER SETUP

Open your terminal and run these commands exactly:

```bash
# Create the main project folder
mkdir hisaab-ai
cd hisaab-ai

# Create the two main folders
mkdir backend
mkdir frontend

# Initialize git
git init
echo "node_modules/\n.env\n__pycache__/\n.venv/" > .gitignore
```

### Backend Setup

```bash
cd backend

# Create a virtual environment (like a clean room just for this project's Python)
python -m venv .venv

# Activate it (you must do this EVERY TIME you open a new terminal for backend work)
# On Mac/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# You'll see (.venv) at the start of your terminal line when it's active

# Install all the packages you need
pip install fastapi uvicorn sqlalchemy supabase python-dotenv
pip install langchain langgraph langchain-groq
pip install openai-whisper easyocr reportlab openpyxl
pip install sentence-transformers qdrant-client redis
pip install httpx python-multipart pydantic-settings

# Save what you installed (so others/Railway can recreate it)
pip freeze > requirements.txt
```

### Frontend Setup

```bash
cd ../frontend

# Create Next.js app
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir

# Install extra packages
npm install @supabase/supabase-js axios zustand recharts
npm install @radix-ui/react-dialog lucide-react
npx shadcn@latest init
```

---

## PHASE 1: THE FOUNDATION

### Goal: WhatsApp sends a message → your server receives it → sends a reply



This is the hardest part to set up but the most important. Once this works, everything else is just adding features.

---

### STEP 1: CREATE YOUR FASTAPI SERVER

Create this file: `backend/main.py`

```python
# backend/main.py
# This is the ENTRY POINT of your entire backend application
# Think of it as the front door of your restaurant

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import webhook, dashboard, health
from core.config import settings

# Create the FastAPI application
app = FastAPI(
    title="HisaabAI Backend",
    description="AI Business Assistant for Pakistani SMEs",
    version="1.0.0"
)

# CORS: allows your Next.js frontend to talk to this backend
# Without this, browsers will block the connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register your route groups (like chapters of a book)
app.include_router(webhook.router, tags=["WhatsApp"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(health.router, tags=["Health"])

# This runs when you start the server
@app.on_event("startup")
async def startup():
    print("🚀 HisaabAI Backend Started")
    print(f"   Environment: {settings.ENVIRONMENT}")
```

---

### STEP 2: CONFIGURATION FILE

This file manages all your secrets and settings.

Create: `backend/core/config.py`

```python
# backend/core/config.py
# pydantic-settings reads values from your .env file automatically
# Think of it as your settings control panel

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    APP_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    SECRET_KEY: str = "change-this-in-production"
    
    # WhatsApp
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "hisaab_verify_2025"
    WHATSAPP_API_VERSION: str = "v19.0"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    DATABASE_URL: str = ""
    
    # AI
    GROQ_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    
    # Redis
    UPSTASH_REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

# Create one instance, import this everywhere
settings = Settings()
```

Create: `backend/.env` (NEVER commit this to GitHub)

```bash
ENVIRONMENT=development
WHATSAPP_TOKEN=your_token_here
WHATSAPP_PHONE_ID=your_phone_id
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

---

### STEP 3: THE WHATSAPP WEBHOOK

This is the endpoint that Meta calls when someone messages your bot.

Create: `backend/api/webhook.py`

```python
# backend/api/webhook.py
# This is the door that WhatsApp knocks on when a user sends a message
# Meta will send a POST request here every single time

from fastapi import APIRouter, Query, BackgroundTasks, Request, HTTPException
from fastapi.responses import PlainTextResponse
from core.config import settings
from services.whatsapp import WhatsAppService
from ai.conversation_handler import handle_message
import json

router = APIRouter()
wa_service = WhatsAppService()

# ============================================================
# STEP 1: Webhook Verification
# Meta calls this ONCE when you first set up the webhook
# It's like Meta saying "hey, are you really there?"
# ============================================================
@router.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        print("✅ WhatsApp webhook verified!")
        return PlainTextResponse(hub_challenge)  # Must return this exact string
    raise HTTPException(status_code=403, detail="Verification failed")


# ============================================================
# STEP 2: Receive Messages
# This is called EVERY TIME a user sends a message
# We process it in the background so we return 200 immediately
# (Meta requires a response in 20 seconds or it retries)
# ============================================================
@router.post("/webhook/whatsapp")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        
        # Extract the actual message from Meta's complex JSON structure
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return {"status": "ok"}  # Status updates, not messages — ignore
        
        message = messages[0]
        user_phone = message.get("from")  # User's phone number
        
        # Mark message as READ (shows blue ticks to user)
        await wa_service.mark_as_read(message["id"])
        
        # Process in background — return 200 immediately to Meta
        background_tasks.add_task(
            process_message,
            user_phone=user_phone,
            message=message
        )
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "ok"}  # Always return 200 to Meta, even on errors


async def process_message(user_phone: str, message: dict):
    """Background task: actually processes the message and sends reply"""
    try:
        # This is where all the magic happens
        response_text = await handle_message(user_phone, message)
        
        if response_text:
            await wa_service.send_text(user_phone, response_text)
            
    except Exception as e:
        print(f"Processing error for {user_phone}: {e}")
        await wa_service.send_text(
            user_phone,
            "Kuch masla ho gaya 😔 Dobara try karein ya 'menu' likhein."
        )
```

---

### STEP 4: WHATSAPP SERVICE (SENDING MESSAGES)

Create: `backend/services/whatsapp.py`

```python
# backend/services/whatsapp.py
# This is your WhatsApp messenger — handles sending all types of messages
# Think of it as your postman

import httpx
from core.config import settings

class WhatsAppService:
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"
        self.phone_id = settings.WHATSAPP_PHONE_ID
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
    
    async def send_text(self, to: str, text: str):
        """Send a simple text message"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/{self.phone_id}/messages",
                headers=self.headers,
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "text",
                    "text": {"body": text}
                }
            )
    
    async def send_document(self, to: str, file_url: str, filename: str, caption: str = ""):
        """Send a PDF or Excel file"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/{self.phone_id}/messages",
                headers=self.headers,
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "document",
                    "document": {
                        "link": file_url,
                        "filename": filename,
                        "caption": caption
                    }
                }
            )
    
    async def mark_as_read(self, message_id: str):
        """Show blue ticks to user"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/{self.phone_id}/messages",
                headers=self.headers,
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message_id
                }
            )
    
    async def download_media(self, media_id: str) -> bytes:
        """Download a voice note or image sent by user"""
        async with httpx.AsyncClient() as client:
            # Step 1: Get the download URL
            resp = await client.get(
                f"{self.base_url}/{media_id}",
                headers=self.headers
            )
            media_url = resp.json()["url"]
            
            # Step 2: Download the actual file
            resp2 = await client.get(media_url, headers=self.headers)
            return resp2.content
```

---

### STEP 5: THE CONVERSATION HANDLER (THE BRAIN)

This is the most important file. Every message passes through here.

Create: `backend/ai/conversation_handler.py`

```python
# backend/ai/conversation_handler.py
#
# THINK OF THIS AS A TRAFFIC CONTROLLER AT AN AIRPORT
# Every message lands here first.
# This controller decides which runway (handler) to send it to.
#
# The flow:
# Message arrives
#   → If user is new: start onboarding
#   → If user is in the middle of a flow: continue that flow
#   → If new request: classify intent → route to correct handler

from core.database import get_supabase
from ai.intent_classifier import classify_intent
from ai.transaction_extractor import extract_transaction
from services.whatsapp import WhatsAppService
from services.transaction_service import TransactionService
import json

wa_service = WhatsAppService()
tx_service = TransactionService()

async def handle_message(user_phone: str, message: dict) -> str:
    """
    Main entry point for ALL incoming WhatsApp messages.
    Returns the text response to send back to the user.
    """
    db = get_supabase()
    
    # ── 1. Extract what type of message this is ──────────────────
    msg_type = message.get("type")  # text, audio, image, document
    
    if msg_type == "text":
        text = message["text"]["body"].strip()
    elif msg_type == "audio":
        # Voice note — transcribe first
        from ai.voice_processor import transcribe_voice
        audio_id = message["audio"]["id"]
        text = await transcribe_voice(audio_id)
        # We'll show user what we heard (confirm flow)
        # For now, treat transcription as text
    elif msg_type == "image":
        # Receipt photo — run OCR
        from ai.ocr_processor import extract_from_receipt
        image_id = message["image"]["id"]
        return await extract_from_receipt(image_id, user_phone)
    else:
        return "Sirf text, voice note, ya tasveer bhejein. 📱"
    
    # ── 2. Check if user exists ───────────────────────────────────
    user = db.table("users").select("*").eq("phone", user_phone).execute()
    
    if not user.data:
        # New user! Start onboarding
        db.table("users").insert({"phone": user_phone}).execute()
        return get_welcome_message()
    
    user_data = user.data[0]
    
    # ── 3. Check if user is in the middle of a flow ───────────────
    # Example: we asked "Customer ka naam?" and are waiting for answer
    state = db.table("conversation_states")\
              .select("*")\
              .eq("user_phone", user_phone)\
              .execute()
    
    if state.data and state.data[0].get("state"):
        current_state = state.data[0]["state"]
        context = state.data[0].get("context", {})
        return await continue_flow(user_phone, text, current_state, context, user_data)
    
    # ── 4. No active flow — classify new intent ───────────────────
    
    # Handle simple commands first (faster than calling AI)
    text_lower = text.lower().strip()
    
    if text_lower in ["menu", "1", "help", "kya kar sakte ho"]:
        return get_main_menu(user_data)
    
    if text_lower in ["excel bhejo", "excel", "sheet"]:
        return await handle_excel_request(user_phone, user_data)
    
    if "report" in text_lower or "summary" in text_lower:
        return await handle_report_request(user_phone, user_data)
    
    # For everything else, use AI to figure out what they want
    intent = await classify_intent(text)
    
    # ── 5. Route to the right handler ────────────────────────────
    if intent == "sale":
        return await handle_sale(user_phone, text, user_data)
    
    elif intent == "expense":
        return await handle_expense(user_phone, text, user_data)
    
    elif intent == "invoice":
        return await start_invoice_flow(user_phone, text, user_data)
    
    elif intent == "udhaar_give":
        return await handle_udhaar_give(user_phone, text, user_data)
    
    elif intent == "udhaar_receive":
        return await handle_udhaar_receive(user_phone, text, user_data)
    
    elif intent == "udhaar_payment":
        return await handle_udhaar_payment(user_phone, text, user_data)
    
    elif intent == "insights":
        return await handle_insights(user_phone, user_data)
    
    else:
        return get_unknown_message()


async def handle_sale(user_phone: str, text: str, user_data: dict) -> str:
    """Extract sale data from text and save it"""
    data = await extract_transaction(text, "sale")
    
    if not data.get("amount"):
        # Ask for clarification
        save_state(user_phone, "awaiting_sale_amount", {"description": data.get("description", "")})
        return "Kitne ki sale hui? (amount likhein)"
    
    # Save to database
    tx = await tx_service.create_transaction(
        business_id=user_data["active_business_id"],
        type="sale",
        amount=data["amount"],
        description=data.get("description", ""),
        customer_name=data.get("customer_or_vendor"),
        payment_method=data.get("payment_method", "cash")
    )
    
    # Get monthly total for context
    monthly_total = await tx_service.get_monthly_total(user_data["active_business_id"], "sale")
    
    return f"""✅ *Sale Record Ho Gayi!*

💰 Amount: Rs. {data['amount']:,.0f}
📝 Item: {data.get('description', 'N/A')}
💳 Payment: {data.get('payment_method', 'Cash').title()}

Is mahine ki total sale: *Rs. {monthly_total:,.0f}*"""


def save_state(user_phone: str, state: str, context: dict):
    """Save the current conversation state to database"""
    db = get_supabase()
    db.table("conversation_states").upsert({
        "user_phone": user_phone,
        "state": state,
        "context": context
    }).execute()


def clear_state(user_phone: str):
    """Clear conversation state after flow is complete"""
    db = get_supabase()
    db.table("conversation_states").upsert({
        "user_phone": user_phone,
        "state": None,
        "context": {}
    }).execute()


def get_welcome_message() -> str:
    return """Assalamualaikum! 👋

Main *HisaabAI* hoon — aapka digital munshi.

Main aapki madad kar sakta hoon:
✅ Sale aur expenses record karna
✅ Invoice banana
✅ Udhaar track karna
✅ Monthly reports banana
✅ Business insights dena

Sab kuch WhatsApp par! 🎉

Shuru karte hain — aapka business ka naam kya hai?"""


def get_main_menu(user_data: dict) -> str:
    business = user_data.get("business_name", "Aapka Business")
    return f"""*{business}* 📊

Kya karna chahte hain?

1️⃣ Sale add karo
2️⃣ Expense add karo
3️⃣ Invoice banao
4️⃣ Udhaar track karo
5️⃣ Report dekho
6️⃣ Excel report
7️⃣ Insights"""


def get_unknown_message() -> str:
    return """Mujhe samajh nahi aaya. 🤔

Kuch examples:
• *Sale:* "aaj 5000 ki sale hui"
• *Expense:* "2000 ka maal khareeda"
• *Invoice:* "invoice banao"
• *Udhaar:* "Ahmed ko 10k udhaar diya"

Ya *menu* likhein."""
```

---

### STEP 6: INTENT CLASSIFIER (AI-POWERED)

Create: `backend/ai/intent_classifier.py`

```python
# backend/ai/intent_classifier.py
#
# This uses AI to figure out WHAT the user wants to do.
# We give the AI a message and it tells us: is this a sale? expense? invoice?
#
# We're using Groq (free) which runs Llama 3.1 at lightning speed.

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.config import settings

# Initialize the AI model — this connects to Groq's API
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.1-70b-versatile",
    temperature=0,  # 0 = deterministic, no creativity needed here
    max_tokens=50   # We only need one word back
)

# The prompt tells AI exactly what we want
INTENT_PROMPT = ChatPromptTemplate.from_template("""
You are an intent classifier for a Pakistani business accounting WhatsApp bot.

Classify the following message into EXACTLY ONE of these categories:
- sale          (recording a sale, money received, something sold)
- expense       (recording an expense, money spent, something purchased for business)
- invoice       (wants to generate an invoice or bill for a customer)
- udhaar_give   (gave credit to someone, customer owes money)
- udhaar_receive (received goods/services on credit, business owes money)
- udhaar_payment (someone paid back udhaar)
- report        (wants to see a summary, report, or month summary)
- excel         (wants an Excel file)
- insights      (wants AI analysis, trends, business advice)
- help          (wants help, menu, or doesn't know what to do)
- unknown       (cannot classify)

Message: {message}

IMPORTANT:
- Message may be in Urdu, Roman Urdu, English, or mixed
- "mila", "aya", "sale hui" = sale
- "gaya", "diya", "khareeda", "kharcha" = expense  
- "invoice", "bill" = invoice
- "udhaar diya", "baad mein lena" = udhaar_give
- "ne diye", "payment aayi" = udhaar_payment

Reply with ONLY the category name. Nothing else.
""")

# Chain: prompt → llm → parse output as string
intent_chain = INTENT_PROMPT | llm | StrOutputParser()

async def classify_intent(message: str) -> str:
    """Returns the intent category as a string"""
    try:
        result = await intent_chain.ainvoke({"message": message})
        intent = result.strip().lower()
        
        # Validate it's one of our known intents
        valid_intents = [
            "sale", "expense", "invoice", "udhaar_give", 
            "udhaar_receive", "udhaar_payment", "report", 
            "excel", "insights", "help", "unknown"
        ]
        
        return intent if intent in valid_intents else "unknown"
        
    except Exception as e:
        print(f"Intent classification error: {e}")
        return "unknown"
```

---

### STEP 7: TRANSACTION EXTRACTOR

Create: `backend/ai/transaction_extractor.py`

```python
# backend/ai/transaction_extractor.py
#
# Once we know the INTENT (e.g., "sale"), this extracts the DETAILS
# "Ahmed ko 45000 ki TV bech di cash mein" →
# { amount: 45000, description: "TV", customer: "Ahmed", payment: "cash" }
#
# We use "structured output" — AI returns JSON, not free text

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.config import settings
import json

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=300
)

EXTRACTION_PROMPT = ChatPromptTemplate.from_template("""
Extract transaction information from this Pakistani business message.
The message may be in Urdu, Roman Urdu, English, or mixed.

Transaction type: {transaction_type}
Message: {message}

Extract and return ONLY a valid JSON object:
{{
  "amount": <number in PKR, null if not found>,
  "description": "<what was sold/bought in English, null if not found>",
  "customer_or_vendor": "<person/company name if mentioned, null if not>",
  "payment_method": "<cash|bank_transfer|easypaisa|jazzcash|udhaar|unknown>",
  "quantity": <number or null>,
  "category": "<for expenses: inventory|utilities|rent|salary|food|transport|other>"
}}

Urdu number guide:
- "ek hazaar" or "1k" or "1000" = 1000
- "paanch hazaar" or "5k" = 5000
- "das hazaar" or "10k" = 10000
- "ek lakh" = 100000

Return ONLY the JSON. No explanation. No markdown.
""")

async def extract_transaction(message: str, transaction_type: str) -> dict:
    """Extract structured transaction data from natural language"""
    try:
        chain = EXTRACTION_PROMPT | llm | JsonOutputParser()
        result = await chain.ainvoke({
            "message": message,
            "transaction_type": transaction_type
        })
        return result
    except Exception as e:
        print(f"Extraction error: {e}")
        return {"amount": None, "description": None}
```

---

### STEP 8: DATABASE CONNECTION

Create: `backend/core/database.py`

```python
# backend/core/database.py
# This connects your FastAPI app to Supabase
# Supabase gives you Postgres + a nice API + Auth + Storage in one

from supabase import create_client, Client
from core.config import settings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """
    Returns Supabase client.
    lru_cache means it creates one connection and reuses it — efficient.
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY  # Use service key for backend (bypasses RLS)
    )
```

---

### STEP 9: RUN YOUR SERVER LOCALLY

```bash
# In your backend folder, with .venv activated:
uvicorn main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# 🚀 HisaabAI Backend Started

# Test it: open http://localhost:8000/docs in browser
# You'll see automatic API documentation (FastAPI's superpower)
```

---

### STEP 10: EXPOSE YOUR LOCAL SERVER TO WHATSAPP

WhatsApp can't reach localhost. ngrok creates a tunnel:

```bash
# In a new terminal:
ngrok http 8000

# You'll see something like:
# Forwarding  https://abc123.ngrok-free.app → http://localhost:8000

# Copy that https URL — you need it for WhatsApp setup
```

---

### STEP 11: SET UP META WHATSAPP API

This is a one-time setup. Follow exactly:

1. Go to developers.facebook.com
2. Create a new App → choose "Business" type
3. Add "WhatsApp" product to your app
4. Go to WhatsApp → API Setup
5. You'll see a test phone number (free to use)
6. Copy your **Phone Number ID** and **Access Token** → put in `.env`
7. Go to "Configuration" → "Webhook"
8. Set Callback URL: `https://abc123.ngrok-free.app/webhook/whatsapp`
9. Set Verify Token: whatever you put in `.env` as `WHATSAPP_VERIFY_TOKEN`
10. Click "Verify and Save"
11. Subscribe to: `messages`

**Test it:** Send a message to the test number → watch your terminal → you should see it printed!

---

## PHASE 2: DOCUMENT GENERATION

### Goal: Generate PDF invoices and Excel reports

---

### PDF INVOICE GENERATOR

Create: `backend/generators/pdf_invoice.py`

```python
# backend/generators/pdf_invoice.py
# ReportLab is the Python library for creating PDFs
# We build the invoice like building a page layout

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
import io
from datetime import datetime

# Define our color scheme
DARK_BLUE = colors.HexColor('#1e3a5f')
LIGHT_GRAY = colors.HexColor('#f5f5f5')
ACCENT_GREEN = colors.HexColor('#2ecc71')

def generate_invoice_pdf(invoice_data: dict) -> bytes:
    """
    Returns PDF as bytes (so we can upload to Supabase Storage)
    
    invoice_data = {
        "invoice_number": "INV-007",
        "business_name": "Khan Electronics",
        "business_phone": "0300-1234567",
        "customer_name": "Ali Traders",
        "items": [
            {"name": "LED TV", "qty": 1, "price": 45000},
            {"name": "HDMI Cable", "qty": 2, "price": 1000},
        ],
        "payment_method": "Cash",
        "date": "2025-06-15"
    }
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        leftMargin=2*cm,
        rightMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ── HEADER ──────────────────────────────────────────────────
    header_data = [
        [
            Paragraph(f"<b>{invoice_data['business_name']}</b>", 
                     ParagraphStyle('biz', fontSize=18, textColor=DARK_BLUE)),
            Paragraph("<b>INVOICE</b>",
                     ParagraphStyle('inv', fontSize=24, textColor=DARK_BLUE, alignment=TA_RIGHT))
        ],
        [
            Paragraph(f"📞 {invoice_data['business_phone']}", styles['Normal']),
            Paragraph(f"#{invoice_data['invoice_number']}<br/>{invoice_data['date']}",
                     ParagraphStyle('num', alignment=TA_RIGHT))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[10*cm, 7*cm])
    header_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ── CUSTOMER INFO ──────────────────────────────────────────
    elements.append(Paragraph("Bill To:", ParagraphStyle('to', fontSize=10, textColor=colors.gray)))
    elements.append(Paragraph(f"<b>{invoice_data['customer_name']}</b>", 
                              ParagraphStyle('cust', fontSize=14)))
    elements.append(Spacer(1, 0.5*cm))
    
    # ── ITEMS TABLE ────────────────────────────────────────────
    table_data = [["Item", "Qty", "Unit Price", "Total"]]
    
    subtotal = 0
    for item in invoice_data["items"]:
        total = item["qty"] * item["price"]
        subtotal += total
        table_data.append([
            item["name"],
            str(item["qty"]),
            f"Rs. {item['price']:,.0f}",
            f"Rs. {total:,.0f}"
        ])
    
    # Total row
    table_data.append(["", "", "TOTAL", f"Rs. {subtotal:,.0f}"])
    
    items_table = Table(table_data, colWidths=[9*cm, 2*cm, 3*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK_BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, LIGHT_GRAY]),
        ('BACKGROUND', (0,-1), (-1,-1), DARK_BLUE),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ── FOOTER ────────────────────────────────────────────────
    elements.append(Paragraph(
        f"💳 Payment Method: {invoice_data['payment_method']}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        "Generated by HisaabAI — aapka digital munshi 🤝",
        ParagraphStyle('footer', fontSize=9, textColor=colors.gray, alignment=TA_CENTER)
    ))
    
    doc.build(elements)
    return buffer.getvalue()
```

---

### EXCEL REPORT GENERATOR

Create: `backend/generators/excel_report.py`

```python
# backend/generators/excel_report.py
# openpyxl creates Excel files
# We build a workbook with multiple sheets

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io
from datetime import datetime

DARK_BLUE = "1E3A5F"
LIGHT_BLUE = "EBF4FF"
GREEN = "2ECC71"
RED = "E74C3C"

def apply_header_style(cell):
    """Make header cells look professional"""
    cell.font = Font(bold=True, color="FFFFFF", size=11)
    cell.fill = PatternFill("solid", fgColor=DARK_BLUE)
    cell.alignment = Alignment(horizontal="center", vertical="center")

def apply_currency(cell, value):
    """Format a number as Pakistani currency"""
    cell.value = value
    cell.number_format = '#,##0.00'

def generate_monthly_excel(data: dict, business_name: str, month: str, year: int) -> bytes:
    """
    data = {
        "sales": [...],
        "expenses": [...],
        "udhaar_given": [...],
        "udhaar_received": [...],
        "invoices": [...]
    }
    """
    wb = openpyxl.Workbook()
    
    # ── SHEET 1: SUMMARY ──────────────────────────────────────
    ws_summary = wb.active
    ws_summary.title = "Summary"
    
    ws_summary.column_dimensions['A'].width = 30
    ws_summary.column_dimensions['B'].width = 20
    
    # Title
    ws_summary['A1'] = f"{business_name} — {month} {year}"
    ws_summary['A1'].font = Font(bold=True, size=16, color=DARK_BLUE)
    ws_summary.merge_cells('A1:B1')
    ws_summary.row_dimensions[1].height = 30
    
    # Calculate totals
    total_sales = sum(t['amount'] for t in data.get('sales', []))
    total_expenses = sum(t['amount'] for t in data.get('expenses', []))
    net_profit = total_sales - total_expenses
    udhaar_outstanding = sum(
        r['total_amount'] - r['paid_amount'] 
        for r in data.get('udhaar_given', []) 
        if r['status'] != 'paid'
    )
    
    rows = [
        ("", ""),
        ("📊 FINANCIAL SUMMARY", ""),
        ("Total Revenue (Sales)", total_sales),
        ("Total Expenses", total_expenses),
        ("Net Profit", net_profit),
        ("", ""),
        ("💳 CREDIT SUMMARY", ""),
        ("Outstanding Udhaar (to collect)", udhaar_outstanding),
    ]
    
    for i, (label, value) in enumerate(rows, start=2):
        ws_summary[f'A{i}'] = label
        if label in ["📊 FINANCIAL SUMMARY", "💳 CREDIT SUMMARY"]:
            ws_summary[f'A{i}'].font = Font(bold=True, size=12)
        if isinstance(value, (int, float)) and value != "":
            apply_currency(ws_summary[f'B{i}'], value)
            if label == "Net Profit":
                color = GREEN if value >= 0 else RED
                ws_summary[f'B{i}'].font = Font(bold=True, color=color, size=12)
    
    # ── SHEET 2: SALES ────────────────────────────────────────
    ws_sales = wb.create_sheet("Sales")
    headers = ["Date", "Description", "Customer", "Payment Method", "Amount (Rs.)"]
    
    for col, header in enumerate(headers, 1):
        cell = ws_sales.cell(row=1, column=col, value=header)
        apply_header_style(cell)
        ws_sales.column_dimensions[get_column_letter(col)].width = 20
    
    for row_idx, sale in enumerate(data.get('sales', []), start=2):
        ws_sales.cell(row=row_idx, column=1, value=str(sale.get('transaction_date', '')))
        ws_sales.cell(row=row_idx, column=2, value=sale.get('description', ''))
        ws_sales.cell(row=row_idx, column=3, value=sale.get('customer_name', ''))
        ws_sales.cell(row=row_idx, column=4, value=sale.get('payment_method', ''))
        apply_currency(ws_sales.cell(row=row_idx, column=5), sale.get('amount', 0))
        
        if row_idx % 2 == 0:
            for col in range(1, 6):
                ws_sales.cell(row=row_idx, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    
    # (Repeat similar pattern for Expenses, Udhaar sheets...)
    # Create "Expenses", "Udhaar Given", "Udhaar Received" sheets similarly
    
    # ── SAVE TO BYTES ─────────────────────────────────────────
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
```

---

## PHASE 3: AI LAYER

### Understanding how LLMs and LangGraph work

---

### WHAT IS AN LLM? (Simple Explanation)

An LLM (Large Language Model) is like a very smart autocomplete. You give it text, it gives text back. Groq hosts Llama 3.1 (Meta's open source model) and lets you use it for free.

```
You send:  "Extract the amount from: Ahmed ko 5000 diye"
AI sends:  "{ amount: 5000, person: 'Ahmed' }"
```

That's all it is. The skill is in writing good prompts.

### WHAT IS LANGCHAIN? (Simple Explanation)

LangChain is a library that makes it easy to:

- Chain prompts together (output of one → input of next)
- Give the AI "tools" it can call (like search, database lookup)
- Build RAG pipelines (AI that answers from your documents)

```python
# Without LangChain (manual):
response = groq_client.chat(messages=[{"role": "user", "content": prompt}])
text = response.choices[0].message.content

# With LangChain (cleaner):
chain = prompt_template | llm | output_parser
result = await chain.ainvoke({"message": user_input})
```

### WHAT IS LANGGRAPH? (Simple Explanation)

LangGraph is like a flowchart for AI agents. You define:

- **Nodes**: functions that do work (one per task)
- **Edges**: which node to go to next (can be conditional)
- **State**: a shared object all nodes can read/write

```
Message arrives
    ↓
[classify_node] → what's the intent?
    ↓
[transaction_node] if sale/expense
[invoice_node]     if invoice
[udhaar_node]      if udhaar
    ↓
[send_response_node] → always runs last
    ↓
END
```

You build this in Phase 6. For now, the simple if/else router is fine.

---

## PHASE 4: VOICE + OCR

### Making the bot understand voice notes and photos

---

### VOICE NOTE PROCESSING

Create: `backend/ai/voice_processor.py`

```python
# backend/ai/voice_processor.py
# Whisper is OpenAI's open source speech-to-text model
# It runs locally on your machine — no API costs
# It's surprisingly good at Urdu

import whisper
import tempfile
import os
from services.whatsapp import WhatsAppService

# Load once at startup (slow to load, fast to run)
# "small" = faster, good enough | "medium" = slower, better Urdu
model = whisper.load_model("small")

wa_service = WhatsAppService()

async def transcribe_voice(audio_id: str) -> str:
    """
    Downloads voice note from WhatsApp, transcribes with Whisper
    Returns the transcribed text
    """
    # Download the audio file
    audio_bytes = await wa_service.download_media(audio_id)
    
    # Save to temp file (Whisper needs a file path)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    
    try:
        # Transcribe — hint that it's likely Urdu/Roman Urdu
        result = model.transcribe(
            tmp_path,
            language="ur",          # Urdu hint
            task="transcribe",
            fp16=False              # Use fp32 for compatibility
        )
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)  # Clean up temp file
```

### OCR RECEIPT PROCESSING

Create: `backend/ai/ocr_processor.py`

```python
# backend/ai/ocr_processor.py
# EasyOCR extracts text from images
# Then we send that text to the LLM to structure it

import easyocr
import tempfile
import os
from services.whatsapp import WhatsAppService
from ai.transaction_extractor import extract_transaction

# Initialize reader (loads ML models — takes a few seconds first time)
reader = easyocr.Reader(['en', 'ur'])  # English + Urdu

wa_service = WhatsAppService()

async def extract_from_receipt(image_id: str, user_phone: str) -> str:
    """
    1. Download image from WhatsApp
    2. Run EasyOCR to extract text
    3. Send text to LLM to structure it
    4. Return confirmation message
    """
    image_bytes = await wa_service.download_media(image_id)
    
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name
    
    try:
        # Extract all text from image
        results = reader.readtext(tmp_path)
        extracted_text = " ".join([text for (_, text, confidence) in results if confidence > 0.3])
        
        if not extracted_text.strip():
            return "Tasveer mein text nahi mili. Clear photo bhejein. 📸"
        
        # Send extracted text to LLM for structuring
        data = await extract_transaction(
            f"Receipt/bill text: {extracted_text}",
            "expense"
        )
        
        # Build confirmation message
        items_text = f"📝 {data.get('description', 'Receipt items')}"
        amount_text = f"Rs. {data['amount']:,.0f}" if data.get('amount') else "Amount nahi mili"
        
        return f"""📸 Receipt scan ho gayi!

{items_text}
💰 Total: {amount_text}

Expense record karoon?
1️⃣ Haan, save karo
2️⃣ Nahi"""
        
    finally:
        os.unlink(tmp_path)
```

---

## PHASE 5: AI MEMORY (VECTOR DATABASE)

### Teaching the AI to remember your business history

---

### WHAT IS A VECTOR DATABASE? (Simple Explanation)

Normal databases store exact data. If you search "Ahmed" you get rows with "Ahmed".

A vector database stores the **meaning** of data. If you search "customer who owes money" it finds Ahmed's record even if the words don't match exactly.

How it works:

1. Text → converted to numbers (called an "embedding") by an AI model
2. Those numbers stored in Qdrant
3. When you search, your query also becomes numbers
4. Qdrant finds the closest matching numbers

```python
# Example: "Ahmed ne 15k udhaar liya" becomes
# [0.234, -0.891, 0.423, 0.112, ...] (768 numbers)
# Stored in Qdrant

# Later, searching "who owes us money?" becomes
# [0.219, -0.876, 0.441, 0.098, ...] (similar numbers)
# Qdrant finds Ahmed's record because the numbers are similar
```

### MEMORY SERVICE

Create: `backend/ai/memory.py`

```python
# backend/ai/memory.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from core.config import settings
import uuid

# Free local embedding model (runs on your machine)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to Qdrant
qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)

COLLECTION_NAME = "business_memory"

def ensure_collection():
    """Create Qdrant collection if it doesn't exist"""
    collections = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in collections:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            # 384 = dimension of all-MiniLM-L6-v2 embeddings
        )

def embed_text(text: str) -> list:
    """Convert text to a list of numbers (embedding)"""
    return embedding_model.encode(text).tolist()

def store_transaction_memory(business_id: str, transaction: dict):
    """
    Store a transaction in vector DB for future AI memory.
    We convert the transaction to a natural language description first.
    """
    ensure_collection()
    
    # Create a natural language description
    description = f"""
    Transaction: {transaction['type']}
    Amount: Rs. {transaction['amount']}
    Description: {transaction.get('description', 'N/A')}
    Customer/Vendor: {transaction.get('customer_name') or transaction.get('vendor_name', 'N/A')}
    Payment: {transaction.get('payment_method', 'cash')}
    Date: {transaction.get('transaction_date')}
    Category: {transaction.get('category', 'N/A')}
    """
    
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(
            id=str(uuid.uuid4()),
            vector=embed_text(description),
            payload={
                "business_id": business_id,
                "transaction_id": str(transaction.get('id', '')),
                "type": transaction['type'],
                "amount": transaction['amount'],
                "description": description,
                "date": str(transaction.get('transaction_date', ''))
            }
        )]
    )

def search_business_memory(business_id: str, query: str, limit: int = 5) -> list:
    """
    Search for relevant past transactions using semantic search.
    query = "customers who paid late"
    Returns: list of relevant transaction records
    """
    ensure_collection()
    
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embed_text(query),
        query_filter={"must": [{"key": "business_id", "match": {"value": business_id}}]},
        limit=limit
    )
    
    return [r.payload for r in results]
```

---

## PHASE 6: LANGGRAPH AGENTS

### The senior engineer upgrade

This phase replaces your simple if/else router with a proper agent network. Only build this AFTER phases 1-5 are working.

```python
# backend/ai/agents/graph.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

class HisaabState(TypedDict):
    """This is the shared state all agents can read and write"""
    user_phone: str
    business_id: str
    raw_message: str
    message_type: str
    intent: Optional[str]
    extracted_data: Optional[dict]
    response_text: Optional[str]
    files_to_send: list
    error: Optional[str]

# Create the graph
workflow = StateGraph(HisaabState)

# Add nodes (each is a function)
workflow.add_node("classify", classify_intent_node)
workflow.add_node("handle_transaction", transaction_node)
workflow.add_node("handle_invoice", invoice_node)
workflow.add_node("handle_udhaar", udhaar_node)
workflow.add_node("handle_insights", insights_node)
workflow.add_node("send_response", send_response_node)

# Set the starting point
workflow.set_entry_point("classify")

# Add conditional routing
workflow.add_conditional_edges(
    "classify",
    route_by_intent,  # function that reads state.intent and returns next node name
    {
        "sale": "handle_transaction",
        "expense": "handle_transaction",
        "invoice": "handle_invoice",
        "udhaar_give": "handle_udhaar",
        "insights": "handle_insights",
        "unknown": "send_response"
    }
)

# All paths lead to send_response
workflow.add_edge("handle_transaction", "send_response")
workflow.add_edge("handle_invoice", "send_response")
workflow.add_edge("handle_udhaar", "send_response")
workflow.add_edge("handle_insights", "send_response")
workflow.add_edge("send_response", END)

# Compile into a runnable
app_graph = workflow.compile()
```

---

## PHASE 7: NEXT.JS DASHBOARD

### You already know this part best

The dashboard is your strongest zone — build it last so the backend is solid.

Key things to know:

```typescript
// Use Supabase client in Next.js
// frontend/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Auth: phone OTP — Supabase handles this natively
// User signs in with phone → gets OTP on WhatsApp → verified
const { data, error } = await supabase.auth.signInWithOtp({
  phone: '+923001234567'
})
```

Dashboard component structure:

```
app/(dashboard)/dashboard/page.tsx
  → fetches: GET /api/dashboard/summary?month=6&year=2025
  → renders: <StatsCards>, <RevenueChart>, <RecentTransactions>
```

---

## N8N AUTOMATION SETUP

n8n is a visual workflow tool. Open it at `http://localhost:5678` after Docker runs.

### How to Create the Udhaar Reminder Workflow:

1. Open n8n → New Workflow
2. Add node: **Schedule Trigger** → set to "Every day at 9:00 AM"
3. Add node: **Supabase** → Query:
  ```sql
   SELECT * FROM udhaar_records 
   WHERE due_date = CURRENT_DATE + 1 
   AND status != 'paid'
  ```
4. Add node: **Loop Over Items** (for each udhaar record)
5. Add node: **HTTP Request** → POST to your FastAPI:
  ```
   URL: http://your-backend/api/send-udhaar-reminder
   Body: { "udhaar_id": "{{ $json.id }}" }
  ```
6. Save and activate

That's it. n8n handles scheduling, you just define the logic visually.

---

## DEPLOYMENT

### When you're ready to go live:

**Backend → Railway:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy from backend folder
cd backend
railway init
railway up

# Set environment variables in Railway dashboard
# Copy everything from your .env
```

**Frontend → Vercel:**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from frontend folder
cd frontend
vercel

# Add environment variables in Vercel dashboard
```

**Update WhatsApp webhook URL:**

- Replace ngrok URL with your Railway URL
- `https://your-app.railway.app/webhook/whatsapp`

---

## YOUR BUILD ORDER (WEEK BY WEEK)

```
WEEK 1-2: Foundation
  Day 1-2:   Create all accounts, install tools
  Day 3-4:   FastAPI setup + database schema in Supabase
  Day 5-6:   WhatsApp webhook receiving messages
  Day 7:     Send basic echo reply back on WhatsApp
  Day 8-9:   User creation + onboarding flow (get business name)
  Day 10-11: Menu system (numbered options)
  Day 12-14: Manual transaction recording (sale/expense) via menu

WEEK 3: AI Transaction Understanding
  Day 15-16: Groq API setup + intent classifier
  Day 17-18: Transaction extractor (structured output)
  Day 19-20: Replace menu with natural language for sale/expense
  Day 21:    Test extensively with Urdu/Roman Urdu sentences

WEEK 4-5: Documents
  Day 22-25: PDF invoice generator
  Day 26-27: Invoice multi-turn flow (ask customer name → payment)
  Day 28-30: Excel report generator
  Day 31-32: File sending via WhatsApp API
  Day 33-35: Supabase Storage for generated files

WEEK 6: Udhaar System
  Day 36-38: Udhaar recording (give + receive)
  Day 39-40: Udhaar payment recording
  Day 41-42: Report + udhaar summary

WEEK 7-8: Voice + OCR
  Day 43-45: Whisper integration + voice note processing
  Day 46-48: EasyOCR + receipt photo processing
  Day 49-50: Confirmation flows for both

WEEK 9-11: AI Memory + Insights
  Day 51-53: Qdrant setup + embedding pipeline
  Day 54-56: Store transactions in vector DB
  Day 57-60: AI insights generation (query vector DB + LLM)
  Day 61-65: Cash flow forecasting

WEEK 12-15: LangGraph Agents
  Day 66-70: Learn LangGraph basics (official docs)
  Day 71-80: Build agent graph replacing conversation handler

WEEK 16-20: Dashboard + Launch Prep
  Day 81-90: Next.js dashboard (all pages)
  Day 91-95: n8n automation workflows
  Day 96-100: Railway + Vercel deployment
  Day 101+:  Find 5 beta users, iterate
```

---

## DEBUGGING GUIDE

### "WhatsApp not calling my webhook"

- Check ngrok is running: `ngrok http 8000`
- Check webhook URL in Meta dashboard is updated
- Check verify token matches exactly
- Run: `curl -X POST http://localhost:8000/webhook/whatsapp -d '{"test":1}'`

### "AI returning wrong intent"

- Print the exact message being sent to Groq
- Test the prompt directly in Groq's playground (console.groq.com)
- Add more examples to your prompt
- Lower temperature to 0

### "Supabase query not working"

- Check RLS policies (might be blocking service key)
- Use Supabase Table Editor to verify data exists
- Print the full response: `print(result.data, result.error)`

### "PDF not generating"

- Test in isolation: `python -c "from generators.pdf_invoice import generate_invoice_pdf; print('OK')"`
- ReportLab errors are usually about missing fonts or wrong data types

### "Whisper not understanding Urdu"

- Try `language=None` (auto-detect) instead of `language="ur"`
- Try the "medium" model for better accuracy
- Urdu voice notes work better with clear speech

---

## WHAT SUCCESS LOOKS LIKE AT EACH PHASE

```
After Phase 1: 
  ✅ Send any message → bot replies
  ✅ First-time user gets welcome + sets up business
  ✅ Can record a sale by choosing "1" from menu

After Phase 2:
  ✅ Say items + customer → get PDF invoice on WhatsApp
  ✅ Say "excel bhejo" → get formatted .xlsx file

After Phase 3:
  ✅ Say "5000 ki sale hui" → saved without any menus
  ✅ Messy Urdu → correctly extracted and saved

After Phase 4:
  ✅ Send voice note → transactions auto-extracted
  ✅ Send receipt photo → amounts auto-pulled out

After Phase 5:
  ✅ "Mera business kaisa chal raha hai" → real AI insight
  ✅ Weekly WhatsApp message with business patterns

After Phase 6:
  ✅ Complex multi-step queries handled by agent network
  ✅ LangGraph state graph in your GitHub README

After Phase 7:
  ✅ Beautiful web dashboard showing all analytics
  ✅ Live demo URL works perfectly for portfolio
  ✅ 5+ real Pakistani businesses using it
```

---

## YOUR TECH LEARNING ORDER

You know Next.js. Here's the order to learn the rest:

```
Week 1:   Python basics for web (FastAPI, async/await, pydantic)
          → fastapi.tiangolo.com (official tutorial, 2 days)

Week 2:   Supabase
          → supabase.com/docs (JavaScript → Python SDK)

Week 3:   LLM basics + prompt engineering
          → Groq playground, try prompts manually first

Week 4:   LangChain basics
          → python.langchain.com/docs/tutorials

Week 5:   Docker basics
          → Just enough to run docker-compose up

Week 8+:  LangGraph
          → langchain-ai.github.io/langgraph (after basics work)
```

---

*Build in public. Post progress every week. The Pakistani dev community is watching — and so are international recruiters.*

*HisaabAI — Aapka digital munshi 🤝*