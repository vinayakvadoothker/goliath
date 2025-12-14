'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import type { WorkItem } from '@/lib/types'
import { formatDistanceToNow } from 'date-fns'

interface ActiveIncidentsListProps {
  workItems: WorkItem[]
}

export function ActiveIncidentsList({ workItems }: ActiveIncidentsListProps) {
  const activeItems = workItems.filter(wi => !wi.jira_issue_key).slice(0, 5)

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
    <Card>
      <CardHeader>
        <CardTitle>Active Incidents</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activeItems.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No active incidents
            </div>
          ) : (
            activeItems.map((item) => (
              <Link
                key={item.id}
                href={`/work-items/${item.id}`}
                className="block p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className={getSeverityColor(item.severity)}>
                      {item.severity.toUpperCase()}
                    </Badge>
                    <div>
                      <div className="font-medium text-sm">{item.service}</div>
                      <div className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {item.id.slice(-6)}
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

