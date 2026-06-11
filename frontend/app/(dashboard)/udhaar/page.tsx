"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { UdhaarRecord } from "@/types";

export default function UdhaarPage() {
  const [tab, setTab] = useState<"customer" | "supplier">("customer");
  const [rows, setRows] = useState<UdhaarRecord[]>([]);

  useEffect(() => {
    api
      .get<UdhaarRecord[]>("/udhaar", { params: { party_type: tab } })
      .then((res) => setRows(res.data));
  }, [tab]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Udhaar Ledger</h1>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setTab("customer")}
          className={`rounded-lg px-4 py-2 text-sm ${
            tab === "customer" ? "bg-primary text-primary-foreground" : "bg-muted"
          }`}
        >
          Given (Customers)
        </button>
        <button
          type="button"
          onClick={() => setTab("supplier")}
          className={`rounded-lg px-4 py-2 text-sm ${
            tab === "supplier" ? "bg-primary text-primary-foreground" : "bg-muted"
          }`}
        >
          Received (Suppliers)
        </button>
      </div>
      <div className="overflow-hidden rounded-xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left">
            <tr>
              <th className="p-3">Party</th>
              <th className="p-3">Total</th>
              <th className="p-3">Paid</th>
              <th className="p-3">Balance</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="p-3">{r.party_name}</td>
                <td className="p-3">Rs. {Number(r.total_amount).toLocaleString()}</td>
                <td className="p-3">Rs. {Number(r.paid_amount).toLocaleString()}</td>
                <td className="p-3">
                  Rs.{" "}
                  {(Number(r.total_amount) - Number(r.paid_amount)).toLocaleString()}
                </td>
                <td className="p-3 capitalize">{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
