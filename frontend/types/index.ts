export interface Business {
  id: string;
  name: string;
  category?: string;
  mode?: string;
  phone?: string;
}

export interface Transaction {
  id: string;
  type: string;
  amount: number;
  description?: string;
  category?: string;
  customer_name?: string;
  vendor_name?: string;
  payment_method?: string;
  transaction_date?: string;
  source?: string;
}

export interface UdhaarRecord {
  id: string;
  party_name: string;
  party_phone?: string;
  party_type: string;
  total_amount: number;
  paid_amount: number;
  status: string;
  due_date?: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_name: string;
  total_amount: number;
  payment_method?: string;
  payment_status?: string;
  pdf_url?: string;
  invoice_date?: string;
}

export interface DashboardSummary {
  business: Business;
  summary: {
    revenue: number;
    expenses: number;
    profit: number;
    udhaar_outstanding: number;
  };
  recent_transactions: Transaction[];
  top_udhaar: UdhaarRecord[];
  month: number;
  year: number;
}
