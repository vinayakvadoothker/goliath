'use client'

import { Badge } from '@/components/ui/badge'
import { formatDistanceToNow } from 'date-fns'
import type { WorkItem } from '@/lib/types'

interface WorkItemHeaderProps {
  workItem: WorkItem
}

export function WorkItemHeader({ workItem }: WorkItemHeaderProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'sev1':
        return 'bg-red-500/20 text-red-400 border-red-500/20'
      case 'sev2':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/20'
      case 'sev3':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/20'
    }
  }

  return (
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        <h1 className="text-3xl font-bold">{workItem.service}</h1>
        <Badge variant="outline" className={getSeverityColor(workItem.severity)}>
          {workItem.severity.toUpperCase()}
        </Badge>
        <Badge variant="outline">
          {workItem.jira_issue_key ? 'Resolved' : 'Open'}
        </Badge>
        <span className="text-sm text-muted-foreground">
          Created {formatDistanceToNow(new Date(workItem.created_at), { addSuffix: true })}
        </span>
      </div>
    </div>
  )
}

