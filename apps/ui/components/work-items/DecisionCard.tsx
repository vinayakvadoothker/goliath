import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfidenceBadge } from "@/components/work-items/ConfidenceBadge";
import { Brain, ArrowRight, UserCheck, ShieldAlert, History } from "lucide-react";

interface DecisionCardProps {
    workItemId: string;
    assignedTo: string;
    confidence: number;
    reasoning: string;
    onOverride: () => void;
}

export function DecisionCard({ workItemId, assignedTo, confidence, reasoning, onOverride }: DecisionCardProps) {
    return (
        <Card className="border-decision/30 bg-decision/5">
            <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                        <Brain className="h-5 w-5 text-decision" />
                        <CardTitle className="text-lg text-decision">Goliath Decision</CardTitle>
                    </div>
                    <ConfidenceBadge confidence={confidence} />
                </div>
                <CardDescription>
                    Automated assignment proposal based on historical performance and availability.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-border">
                    <div className="flex items-center gap-3">
                        <div className="text-sm font-medium text-muted-foreground">Assign To:</div>
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-full bg-primary/20 grid place-items-center font-bold text-primary">
                                {assignedTo.substring(0, 2).toUpperCase()}
                            </div>
                            <span className="font-bold text-lg">{assignedTo}</span>
                        </div>
                    </div>
                    <Badge variant="outline" className="text-xs">Top Candidate</Badge>
                </div>

                <div className="space-y-2">
                    <h4 className="text-sm font-semibold flex items-center gap-2">
                        <History className="h-4 w-4 text-muted-foreground" />
                        Reasoning Trace
                    </h4>
                    <div className="p-3 text-sm rounded-md bg-muted/50 font-mono text-muted-foreground whitespace-pre-wrap">
                        {reasoning}
                    </div>
                </div>
            </CardContent>
            <CardFooter className="flex justify-between border-t bg-muted/20 p-4">
                <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3" />
                    Audit ID: {workItemId}-DEC-001
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" size="sm" onClick={onOverride} className="border-red-500/30 hover:bg-red-500/10 hover:text-red-500">
                        Override Decision
                    </Button>
                    <Button size="sm" className="bg-decision hover:bg-decision/90 text-decision-foreground">
                        Confirm Assignment <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </CardFooter>
        </Card>
    );
}
