interface Props {
  revenue: number;
  expenses: number;
  profit: number;
  udhaar: number;
}

function Card({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "green" | "red" | "blue" | "orange";
}) {
  const tones = {
    green: "border-emerald-200 bg-emerald-50 text-emerald-900",
    red: "border-rose-200 bg-rose-50 text-rose-900",
    blue: "border-sky-200 bg-sky-50 text-sky-900",
    orange: "border-amber-200 bg-amber-50 text-amber-900",
  };
  return (
    <div className={`rounded-xl border p-5 ${tones[tone]}`}>
      <p className="text-sm opacity-80">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}

export function StatsCards({ revenue, expenses, profit, udhaar }: Props) {
  const fmt = (n: number) => `Rs. ${n.toLocaleString("en-PK")}`;
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card label="This Month Revenue" value={fmt(revenue)} tone="green" />
      <Card label="This Month Expenses" value={fmt(expenses)} tone="red" />
      <Card label="Net Profit" value={fmt(profit)} tone="blue" />
      <Card label="Udhaar Outstanding" value={fmt(udhaar)} tone="orange" />
    </div>
  );
}
