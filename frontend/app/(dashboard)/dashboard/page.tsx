"use client";

import { useEffect, useState } from "react";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { api } from "@/lib/api";
import type { DashboardSummary } from "@/types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<DashboardSummary>("/dashboard/summary")
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail ?? "Failed to load dashboard"));
  }, []);

  if (error) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
        {error}
      </div>
    );
  }

  if (!data) {
    return <p className="text-muted-foreground">Loading dashboard...</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">{data.business.name}</h1>
        <p className="text-sm text-muted-foreground">
          {data.month}/{data.year} overview
        </p>
      </div>
      <StatsCards
        revenue={data.summary.revenue}
        expenses={data.summary.expenses}
        profit={data.summary.profit}
        udhaar={data.summary.udhaar_outstanding}
      />
      <section>
        <h2 className="mb-3 text-lg font-medium">Recent Transactions</h2>
        <div className="overflow-hidden rounded-xl border">
          <table className="w-full text-sm">
            <thead className="bg-muted text-left">
              <tr>
                <th className="p-3">Date</th>
                <th className="p-3">Type</th>
                <th className="p-3">Description</th>
                <th className="p-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_transactions.map((tx) => (
                <tr key={tx.id} className="border-t">
                  <td className="p-3">{tx.transaction_date}</td>
                  <td className="p-3 capitalize">{tx.type}</td>
                  <td className="p-3">{tx.description ?? "—"}</td>
                  <td className="p-3 text-right">Rs. {Number(tx.amount).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section>
        <h2 className="mb-3 text-lg font-medium">Top Udhaar</h2>
        <ul className="space-y-2">
          {data.top_udhaar.map((u) => (
            <li
              key={u.id}
              className="flex justify-between rounded-lg border px-4 py-3 text-sm"
            >
              <span>{u.party_name}</span>
              <span>
                Rs.{" "}
                {(
                  Number(u.total_amount) - Number(u.paid_amount ?? 0)
                ).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
