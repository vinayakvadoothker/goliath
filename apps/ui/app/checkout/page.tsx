"use client";

import { useEffect, useState, useCallback } from "react";
import { loadStripe } from "@stripe/stripe-js";
import {
  EmbeddedCheckoutProvider,
  EmbeddedCheckout,
} from "@stripe/react-stripe-js";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export default function CheckoutPage() {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchClientSecret = useCallback(async () => {
    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan: "Pro", billingCycle: "monthly" }),
      });
      const data = await response.json();
      if (data.clientSecret) {
        setClientSecret(data.clientSecret);
      } else {
        setError(data.error || "Failed to initialize checkout");
      }
    } catch (err) {
      setError("Failed to connect to payment service");
    }
  }, []);

  useEffect(() => {
    fetchClientSecret();
  }, [fetchClientSecret]);

  return (
    <div className="min-h-[80vh] flex flex-col animate-in fade-in duration-500">
      {/* Header */}
      <div className="mb-6">
        <Link href="/billing">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Billing
          </Button>
        </Link>
        <h1 className="text-3xl font-bold tracking-tight mt-4">Upgrade to Pro</h1>
        <p className="text-muted-foreground">Complete your subscription to unlock all Pro features.</p>
      </div>

      {/* Checkout Container */}
      <Card className="flex-1 p-6 bg-[#0f0f0f] border-border overflow-hidden">
        {error ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => { setError(null); fetchClientSecret(); }}>
              Try Again
            </Button>
          </div>
        ) : !clientSecret ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="stripe-checkout-wrapper">
            <EmbeddedCheckoutProvider
              stripe={stripePromise}
              options={{ clientSecret }}
            >
              <EmbeddedCheckout />
            </EmbeddedCheckoutProvider>
          </div>
        )}
      </Card>

      {/* Plan Summary */}
      <div className="mt-6 p-4 rounded-lg bg-primary/5 border border-primary/20">
        <div className="flex justify-between items-center">
          <div>
            <p className="font-medium">Centra Pro Plan</p>
            <p className="text-sm text-muted-foreground">Billed monthly</p>
          </div>
          <p className="text-2xl font-bold">$49<span className="text-sm text-muted-foreground">/mo</span></p>
        </div>
      </div>
    </div>
  );
}
