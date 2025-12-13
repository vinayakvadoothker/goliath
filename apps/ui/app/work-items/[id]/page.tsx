"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator"; // Need to create Separator or just use hr
import { ArrowLeft, Clock, Activity, FileText, Share2, Info } from "lucide-react";
import Link from "next/link";
import { DecisionCard } from "@/components/work-items/DecisionCard";
import { EvidenceBullet } from "@/components/work-items/EvidenceBullet";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { OverrideModal } from "@/components/work-items/OverrideModal";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function WorkItemDetailPage({ params }: { params: { id: string } }) {
    const [showOverride, setShowOverride] = useState(false);

    // Mock Data
    const workItem = {
        id: params.id || "WI-3921",
        title: "High latency in payments-api",
        description: "API latency p99 exceeded 2000ms threshold for > 5 minutes. Source identified as database connection pool exhaustion in payments-service deployment.",
        service: "payments-api",
        severity: "sev1",
        status: "Open",
        created: "2023-10-27T10:30:00Z",
    };

    const decision = {
        assignedTo: "pager-bot",
        confidence: 0.98,
        reasoning: "1. Service 'payments-api' has active on-call rotation: [Primary: pager-bot].\n2. Incident matches 'db-connection' cluster pattern seen in WI-3402.\n3. 'pager-bot' successfully resolved WI-3402 in 12m.\n4. Human load check: Sarah (On-Call) is currently handling WI-3918 (Sev2).",
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex flex-col gap-4">
                <Link href="/work-items" className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1">
                    <ArrowLeft className="h-4 w-4" /> Back to List
                </Link>
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    <div className="space-y-2">
                        <div className="flex items-center gap-3">
                            <h1 className="text-3xl font-bold tracking-tight">{workItem.id}: {workItem.title}</h1>
                            <SeverityBadge severity={workItem.severity as any} />
                            <Badge variant="outline">{workItem.status}</Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                                <Activity className="h-4 w-4" />
                                {workItem.service}
                            </div>
                            <div className="flex items-center gap-1">
                                <Clock className="h-4 w-4" />
                                Created 10 mins ago
                            </div>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                            <Share2 className="mr-2 h-4 w-4" /> Share
                        </Button>
                        <Button variant="outline" size="sm">
                            <FileText className="mr-2 h-4 w-4" /> Logs
                        </Button>
                    </div>
                </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="md:col-span-2 space-y-6">
                    {/* Description */}
                    <div className="p-4 rounded-lg border bg-card">
                        <h3 className="font-semibold mb-2">Description</h3>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                            {workItem.description}
                        </p>
                    </div>

                    {/* Decision Card */}
                    <DecisionCard
                        workItemId={workItem.id}
                        assignedTo={decision.assignedTo}
                        confidence={decision.confidence}
                        reasoning={decision.reasoning}
                        onOverride={() => setShowOverride(true)}
                    />

                    {/* Evidence Section */}
                    <div className="space-y-3">
                        <h3 className="font-semibold text-lg">Supporting Evidence</h3>
                        <div className="bg-card rounded-lg border p-1">
                            <EvidenceBullet
                                type="on_call"
                                text="Target user is currently Primary On-Call for 'payments-api'"
                                source="PagerDuty"
                            />
                            <EvidenceBullet
                                type="similar_incident"
                                text="Resolved similar incident (92% similarity) last week"
                                timeWindow="7 days ago"
                                source="Knowledge Graph"
                            />
                            <EvidenceBullet
                                type="low_load"
                                text="Current cognitive load is low (0 active tickets)"
                                source="Jira"
                            />
                        </div>
                    </div>
                </div>

                {/* Sidebar Context */}
                <div className="space-y-6">
                    <div className="rounded-lg border bg-card p-4 space-y-4">
                        <h3 className="font-semibold text-sm uppercase text-muted-foreground">Context</h3>

                        <div className="space-y-3">
                            <div className="text-sm">
                                <span className="text-muted-foreground block mb-1">Related Services</span>
                                <div className="flex flex-wrap gap-2">
                                    <Badge variant="secondary">database</Badge>
                                    <Badge variant="secondary">auth-service</Badge>
                                </div>
                            </div>

                            <div className="text-sm">
                                <span className="text-muted-foreground block mb-1">Impact Analysis</span>
                                <Alert variant="warning" className="py-2">
                                    <AlertTitle className="text-xs font-bold">Customer Facing</AlertTitle>
                                    <AlertDescription className="text-xs">
                                        High probability of checkout failures.
                                    </AlertDescription>
                                </Alert>
                            </div>
                        </div>
                    </div>

                    <div className="rounded-lg border bg-card p-4 space-y-4">
                        <h3 className="font-semibold text-sm uppercase text-muted-foreground">Similar Incidents</h3>
                        <div className="space-y-2">
                            <Link href="#" className="block text-sm hover:underline text-primary">WI-3402: DB Pool Exhaustion</Link>
                            <Link href="#" className="block text-sm hover:underline text-primary">WI-3110: Latency Spike</Link>
                        </div>
                    </div>
                </div>
            </div>

            <OverrideModal
                isOpen={showOverride}
                onClose={() => setShowOverride(false)}
                currentAssignee={decision.assignedTo}
                onSubmit={(data) => console.log("Overlay Submit", data)}
            />
        </div>
    );
}
