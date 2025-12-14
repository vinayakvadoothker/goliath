'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ExternalLink } from 'lucide-react'
import type { WorkItem } from '@/lib/types'

interface ActionsPanelProps {
  workItem: WorkItem
  hasDecision: boolean
  onOverride: () => void
  onMarkResolved: () => void
}

export function ActionsPanel({
  workItem,
  hasDecision,
  onOverride,
  onMarkResolved,
}: ActionsPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {hasDecision && (
          <Button className="w-full" onClick={onOverride}>
            Override Assignment
          </Button>
        )}
        <Button variant="outline" className="w-full" onClick={onMarkResolved}>
          Mark Resolved
        </Button>
        {workItem.jira_issue_key && (
          <Button
            variant="outline"
            className="w-full"
            onClick={() => {
              window.open(`https://jira.example.com/browse/${workItem.jira_issue_key}`, '_blank')
            }}
          >
            View in Jira <ExternalLink className="ml-2 h-4 w-4" />
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

