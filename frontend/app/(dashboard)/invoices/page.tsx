"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Invoice } from "@/types";

export default function InvoicesPage() {
  const [rows, setRows] = useState<Invoice[]>([]);

  useEffect(() => {
    api.get<Invoice[]>("/invoices").then((res) => setRows(res.data));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Invoices</h1>
      <div className="overflow-hidden rounded-xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left">
            <tr>
              <th className="p-3">#</th>
              <th className="p-3">Customer</th>
              <th className="p-3">Date</th>
              <th className="p-3">Total</th>
              <th className="p-3">Status</th>
              <th className="p-3">PDF</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((inv) => (
              <tr key={inv.id} className="border-t">
                <td className="p-3">{inv.invoice_number}</td>
                <td className="p-3">{inv.customer_name}</td>
                <td className="p-3">{inv.invoice_date}</td>
                <td className="p-3">Rs. {Number(inv.total_amount).toLocaleString()}</td>
                <td className="p-3">{inv.payment_status}</td>
                <td className="p-3">
                  {inv.pdf_url ? (
                    <a
                      href={inv.pdf_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sky-600 underline"
                    >
                      Download
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
