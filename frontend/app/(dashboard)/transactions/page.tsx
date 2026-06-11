"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Transaction } from "@/types";

export default function TransactionsPage() {
  const [rows, setRows] = useState<Transaction[]>([]);
  const [filter, setFilter] = useState<string>("");

  useEffect(() => {
    const params = filter ? { type: filter } : {};
    api.get<Transaction[]>("/transactions", { params }).then((res) => setRows(res.data));
  }, [filter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Transactions</h1>
        <select
          className="rounded-lg border px-3 py-2 text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All</option>
          <option value="sale">Sales</option>
          <option value="expense">Expenses</option>
        </select>
      </div>
      <div className="overflow-hidden rounded-xl border">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left">
            <tr>
              <th className="p-3">Date</th>
              <th className="p-3">Type</th>
              <th className="p-3">Description</th>
              <th className="p-3">Payment</th>
              <th className="p-3">Source</th>
              <th className="p-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((tx) => (
              <tr key={tx.id} className="border-t">
                <td className="p-3">{tx.transaction_date}</td>
                <td className="p-3 capitalize">{tx.type}</td>
                <td className="p-3">{tx.description ?? "—"}</td>
                <td className="p-3">{tx.payment_method ?? "—"}</td>
                <td className="p-3">{tx.source ?? "whatsapp"}</td>
                <td className="p-3 text-right">Rs. {Number(tx.amount).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
