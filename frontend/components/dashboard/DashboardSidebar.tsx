"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/transactions", label: "Transactions" },
  { href: "/udhaar", label: "Udhaar" },
  { href: "/invoices", label: "Invoices" },
  { href: "/settings", label: "Settings" },
];

export function DashboardSidebar() {
  const pathname = usePathname();
  return (
    <aside className="flex w-56 flex-col border-r border-border bg-card p-4">
      <div className="mb-8">
        <p className="text-lg font-semibold text-foreground">HisaabAI</p>
        <p className="text-xs text-muted-foreground">Digital munshi</p>
      </div>
      <nav className="flex flex-1 flex-col gap-1">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-lg px-3 py-2 text-sm transition-colors ${
                active
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
