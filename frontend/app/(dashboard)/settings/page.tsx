"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { supabase } from "@/lib/supabase";

export default function SettingsPage() {
  const [me, setMe] = useState<{
    phone?: string;
    business?: { name?: string; category?: string; phone?: string };
  } | null>(null);

  useEffect(() => {
    api.get("/me").then((res) => setMe(res.data));
  }, []);

  async function signOut() {
    await supabase.auth.signOut();
    window.location.href = "/login";
  }

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold">Settings</h1>
      {me && (
        <div className="space-y-3 rounded-xl border p-5 text-sm">
          <p>
            <span className="text-muted-foreground">Phone:</span> {me.phone}
          </p>
          <p>
            <span className="text-muted-foreground">Business:</span>{" "}
            {me.business?.name ?? "—"}
          </p>
          <p>
            <span className="text-muted-foreground">Category:</span>{" "}
            {me.business?.category ?? "—"}
          </p>
        </div>
      )}
      <Button variant="outline" onClick={signOut}>
        Sign out
      </Button>
    </div>
  );
}
