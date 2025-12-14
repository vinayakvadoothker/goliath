'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { ChevronDown } from 'lucide-react'
import type { Decision, Candidate } from '@/lib/types'

interface DecisionCardProps {
  decision: Decision
  assigneeName?: string
  backupNames?: string[]
  evidence?: Array<{
    type: string
    text: string
    time_window: string
    source: string
  }>
}

export function DecisionCard({ decision, assigneeName, backupNames, evidence }: DecisionCardProps) {
  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.7) return 'bg-green-500'
    if (confidence > 0.4) return 'bg-yellow-500'
    return 'bg-red-500'
  }

    return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Decision</CardTitle>
          <Badge variant="outline" className="bg-purple-500/20 text-purple-400">
            {(decision.confidence * 100).toFixed(1)}% Confidence
          </Badge>
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
        {/* Primary Assignee */}
        <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="text-lg">
              {assigneeName?.charAt(0).toUpperCase() || decision.primary_human_id.slice(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <h3 className="text-xl font-semibold">{assigneeName || decision.primary_human_id}</h3>
            <p className="text-sm text-muted-foreground">Primary Assignee</p>
                        </div>
                    </div>

        {/* Confidence */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Confidence</span>
            <span>{(decision.confidence * 100).toFixed(1)}%</span>
          </div>
          <Progress value={decision.confidence * 100} className="h-2" />
                </div>

        <Separator />

        {/* Backup Assignees */}
        {decision.backup_human_ids.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Backup Assignees</h4>
            <div className="flex gap-2 flex-wrap">
              {decision.backup_human_ids.map((id, idx) => (
                <Badge key={id} variant="outline">
                  {backupNames?.[idx] || id}
                </Badge>
              ))}
                    </div>
                </div>
        )}

        {/* Evidence */}
        {evidence && evidence.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger className="flex items-center gap-2 w-full text-left">
              <ChevronDown className="h-4 w-4" />
              <span className="font-semibold">Evidence ({evidence.length})</span>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-4 space-y-2">
              <ul className="list-disc list-inside space-y-1 text-sm">
                {evidence.map((ev, i) => (
                  <li key={i}>
                    <span className="font-medium">{ev.type}:</span> {ev.text}
                    {ev.time_window && <span className="text-muted-foreground"> ({ev.time_window})</span>}
                    {ev.source && <span className="text-muted-foreground"> [{ev.source}]</span>}
                  </li>
                ))}
              </ul>
            </CollapsibleContent>
          </Collapsible>
        )}
            </CardContent>
        </Card>
  )
}
