"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState("+92");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendOtp(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const { error: err } = await supabase.auth.signInWithOtp({ phone });
    setLoading(false);
    if (err) {
      setError(err.message);
      return;
    }
    setStep("otp");
  }

  async function verifyOtp(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const { error: err } = await supabase.auth.verifyOtp({
      phone,
      token: otp,
      type: "sms",
    });
    setLoading(false);
    if (err) {
      setError(err.message);
      return;
    }
    router.push("/dashboard");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 p-6">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/95 p-8 shadow-xl">
        <h1 className="text-2xl font-semibold text-slate-900">HisaabAI Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">
          Sign in with the same phone you use on WhatsApp. Complete bot onboarding first.
        </p>
        {step === "phone" ? (
          <form onSubmit={sendOtp} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-700">Phone (E.164)</label>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+923001234567"
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Sending..." : "Send OTP"}
            </Button>
          </form>
        ) : (
          <form onSubmit={verifyOtp} className="mt-6 space-y-4">
            <label className="block text-sm font-medium text-slate-700">OTP Code</label>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder="123456"
            />
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Verifying..." : "Verify & Enter"}
            </Button>
          </form>
        )}
        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      </div>
    </div>
  );
}
