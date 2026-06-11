import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 px-6 text-white">
      <div className="max-w-2xl text-center">
        <p className="text-sm uppercase tracking-widest text-emerald-300/80">
          WhatsApp-first business assistant
        </p>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
          HisaabAI
        </h1>
        <p className="mt-4 text-lg text-slate-300">
          Your digital munshi on WhatsApp — sales, expenses, udhaar, invoices, and
          reports in Urdu, Roman Urdu, or English.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Button asChild size="lg">
            <Link href="/login">Open Dashboard</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="border-white/30 text-white">
            <a href="https://developers.facebook.com/docs/whatsapp/cloud-api">
              WhatsApp Setup Docs
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
}
