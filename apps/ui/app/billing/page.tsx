"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Building2, Sparkles, CheckCircle2, XCircle } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "$0",
    period: "/month",
    description: "For small teams getting started",
    features: [
      "Up to 5 team members",
      "100 work items/month",
      "Basic routing",
      "Email support",
    ],
    current: true,
    popular: false,
  },
  {
    name: "Pro",
    price: "$49",
    period: "/month",
    description: "For growing teams that need more",
    features: [
      "Up to 25 team members",
      "Unlimited work items",
      "Advanced AI routing",
      "Priority support",
      "Custom integrations",
      "Analytics dashboard",
    ],
    current: false,
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For large organizations",
    features: [
      "Unlimited team members",
      "Unlimited work items",
      "Custom AI models",
      "Dedicated support",
      "SLA guarantee",
      "On-premise option",
      "SSO & SAML",
    ],
    current: false,
    popular: false,
  },
];

export default function BillingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const router = useRouter();
  const searchParams = useSearchParams();
  const success = searchParams.get("success");
  const canceled = searchParams.get("canceled");

  function handleUpgrade(planName: string) {
    if (planName === "Pro") {
      router.push("/checkout");
    }
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing & Plans</h1>
        <p className="text-muted-foreground">Manage your subscription and billing information.</p>
      </div>

      {/* Success/Cancel Messages */}
      {success && (
        <Card className="border-green-500/50 bg-green-500/10">
          <CardContent className="flex items-center gap-3 py-4">
            <CheckCircle2 className="h-5 w-5 text-green-500" />
            <p className="text-green-500 font-medium">Payment successful! Your Pro plan is now active.</p>
          </CardContent>
        </Card>
      )}
      
      {canceled && (
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="flex items-center gap-3 py-4">
            <XCircle className="h-5 w-5 text-yellow-500" />
            <p className="text-yellow-500 font-medium">Payment canceled. Your plan remains unchanged.</p>
          </CardContent>
        </Card>
      )}

      {/* Billing Cycle Toggle */}
      <div className="flex items-center justify-center gap-4">
        <span className={billingCycle === "monthly" ? "text-white" : "text-muted-foreground"}>Monthly</span>
        <button
          onClick={() => setBillingCycle(billingCycle === "monthly" ? "yearly" : "monthly")}
          className="relative w-14 h-7 bg-white/10 rounded-full transition-colors"
        >
          <div className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-transform ${billingCycle === "yearly" ? "translate-x-8" : "translate-x-1"}`} />
        </button>
        <span className={billingCycle === "yearly" ? "text-white" : "text-muted-foreground"}>
          Yearly
          <Badge variant="secondary" className="ml-2 text-xs">Save 20%</Badge>
        </span>
      </div>

      {/* Pricing Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <Card
            key={plan.name}
            className={`relative ${plan.popular ? "border-primary shadow-lg shadow-primary/10" : ""} ${plan.current ? "bg-primary/5 border-primary/50" : ""}`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <Badge className="bg-primary text-primary-foreground">
                  <Sparkles className="mr-1 h-3 w-3" />
                  Most Popular
                </Badge>
              </div>
            )}
            <CardHeader className="pt-8">
              <CardTitle className="flex items-center gap-2">
                {plan.name === "Enterprise" ? <Building2 className="h-5 w-5" /> : null}
                {plan.name}
                {plan.current && <Badge variant="secondary" className="text-xs">Current</Badge>}
              </CardTitle>
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-bold">
                  {billingCycle === "yearly" && plan.price !== "Custom"
                    ? `$${Math.round(parseInt(plan.price.replace("$", "")) * 0.8)}`
                    : plan.price}
                </span>
                <span className="text-muted-foreground">{plan.period}</span>
              </div>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm">
                    <Check className="h-4 w-4 text-primary flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              {plan.name === "Enterprise" ? (
                <a href="mailto:vinvadoothker@gmail.com" className="block">
                  <Button className="w-full" variant="secondary">
                    Contact Sales
                  </Button>
                </a>
              ) : plan.current ? (
                <Button className="w-full" variant="outline" disabled>
                  Current Plan
                </Button>
              ) : (
                <Button
                  className="w-full"
                  variant={plan.popular ? "default" : "secondary"}
                  onClick={() => handleUpgrade(plan.name)}
                >
                  Upgrade
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
