# HisaabAI

WhatsApp-first AI business assistant for Pakistani SMEs — sales, expenses, udhaar, invoices, and reports.

See **[ARCHITECTURE.md](./ARCHITECTURE.md)** for diagrams and system design.

## Quick start

### 1. Supabase

1. Create a project at [supabase.com](https://supabase.com).
2. Run [`supabase/schema.sql`](./supabase/schema.sql) in the SQL editor.
3. Create a storage bucket: `hisaab-files` (public or signed URLs).
4. Enable **Phone** auth provider for dashboard OTP.
5. Copy **Project URL** into both env files (replace `YOUR_PROJECT_REF`).

### 2. Environment

- `backend/.env` — already created; **set `SUPABASE_URL`** and `DATABASE_URL` from your project.
- `frontend/.env.local` — set `NEXT_PUBLIC_SUPABASE_URL` to the same URL.

### 3. Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs for API documentation.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. WhatsApp (Meta)

1. [developers.facebook.com](https://developers.facebook.com) → WhatsApp → API Setup.
2. Webhook URL: `https://<your-tunnel>/webhook/whatsapp`
3. Verify token: `hisaab_verify_2025` (must match `.env`)
4. Subscribe to **messages**.

Use ngrok or similar to tunnel port 8000 during local testing.

### 6. Optional Docker services

```bash
docker compose up -d
```

Runs Qdrant (6333), Redis (6379), n8n (5678).

## Security note

Never commit `.env` files. If API keys were shared in chat, **rotate them** in Meta, Supabase, Groq, and Resend dashboards.
