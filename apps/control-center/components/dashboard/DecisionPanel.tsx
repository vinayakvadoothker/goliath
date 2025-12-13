"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Decision } from "@/types"

interface DecisionPanelProps {
  decision?: Decision
}

export function DecisionPanel({ decision }: DecisionPanelProps) {
  if (!decision) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Latest Decision</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">No decision made yet</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Latest Decision</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <Avatar>
            <AvatarFallback>{decision.assignee_name.charAt(0)}</AvatarFallback>
          </Avatar>
          <div>
            <div className="font-semibold">{decision.assignee_name}</div>
            <div className="text-sm text-muted-foreground">Primary Assignee</div>
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Confidence</span>
            <span>{(decision.confidence * 100).toFixed(1)}%</span>
          </div>
          <Progress value={decision.confidence * 100} className="h-2" />
        </div>

        <Separator />

        <div className="space-y-2">
          <div className="font-semibold text-sm">Evidence</div>
          <ul className="list-disc list-inside space-y-1 text-sm">
            {decision.evidence.map((ev, idx) => (
              <li key={idx}>{ev}</li>
            ))}
          </ul>
        </div>

        {decision.constraints && decision.constraints.length > 0 && (
          <>
            <Separator />
            <div className="space-y-2">
              <div className="font-semibold text-sm">Constraints</div>
              <div className="space-y-1">
                {decision.constraints.map((constraint, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-sm">
                    <span className={constraint.passed ? "text-primary" : "text-error"}>
                      {constraint.passed ? "✓" : "✗"}
                    </span>
                    <span>{constraint.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

