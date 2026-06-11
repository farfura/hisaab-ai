-- HisaabAI — run in Supabase SQL Editor
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    active_business_id UUID,
    onboarding_complete BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    mode VARCHAR(20) DEFAULT 'business',
    phone VARCHAR(20),
    address TEXT,
    logo_url TEXT,
    currency VARCHAR(3) DEFAULT 'PKR',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE users
    DROP CONSTRAINT IF EXISTS users_active_business_id_fkey;
ALTER TABLE users
    ADD CONSTRAINT users_active_business_id_fkey
    FOREIGN KEY (active_business_id) REFERENCES businesses(id) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    customer_name VARCHAR(200),
    vendor_name VARCHAR(200),
    payment_method VARCHAR(50),
    reference_number VARCHAR(100),
    notes TEXT,
    transaction_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(20) DEFAULT 'whatsapp'
);

CREATE TABLE IF NOT EXISTS udhaar_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    party_name VARCHAR(200) NOT NULL,
    party_phone VARCHAR(20),
    party_type VARCHAR(10) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    paid_amount DECIMAL(12, 2) DEFAULT 0,
    due_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_reminder_sent TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS udhaar_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    udhaar_id UUID REFERENCES udhaar_records(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date DATE DEFAULT CURRENT_DATE,
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoices (
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
    payment_status VARCHAR(20) DEFAULT 'unpaid',
    due_date DATE,
    pdf_url TEXT,
    notes TEXT,
    invoice_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    item_name VARCHAR(300) NOT NULL,
    quantity DECIMAL(10, 2) DEFAULT 1,
    unit_price DECIMAL(12, 2) NOT NULL,
    total_price DECIMAL(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_phone VARCHAR(20) UNIQUE NOT NULL,
    state VARCHAR(100),
    context JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS message_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_phone VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    message_type VARCHAR(20),
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_business_date ON transactions(business_id, transaction_date);
CREATE INDEX IF NOT EXISTS idx_udhaar_business ON udhaar_records(business_id);
CREATE INDEX IF NOT EXISTS idx_invoices_business ON invoices(business_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_phone ON message_logs(user_phone);

-- RLS (enable in Supabase dashboard after policies)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE udhaar_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE udhaar_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
