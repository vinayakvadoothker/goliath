'use client'

import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { formatDistanceToNow } from 'date-fns'
import { useDecision } from '@/lib/queries'
import type { WorkItem } from '@/lib/types'

interface RecentDecisionItemProps {
  workItem: WorkItem
}

export function RecentDecisionItem({ workItem }: RecentDecisionItemProps) {
  const { data: decision } = useDecision(workItem.id)

  return (
    <Link href={`/work-items/${workItem.id}`} className="block">
      <div className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer group">
        <div className="flex items-center gap-4">
          <div className="h-9 w-9 bg-primary/20 text-primary rounded-full grid place-items-center font-bold text-xs group-hover:bg-primary/30 transition-colors">
            {workItem.id.slice(-2).toUpperCase()}
          </div>
          <div>
            <div className="font-medium group-hover:text-primary transition-colors">
              {workItem.description.substring(0, 50)}
              {workItem.description.length > 50 ? '...' : ''}
            </div>
            <div className="text-xs text-muted-foreground flex items-center gap-2">
              <span>{workItem.service}</span>
              <span>•</span>
              <span>{formatDistanceToNow(new Date(workItem.created_at), { addSuffix: true })}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {decision ? (
            <>
              <Badge variant="outline" className="bg-purple-500/20 text-purple-400 border-purple-500/20">
                Assigned
              </Badge>
              <div className="flex -space-x-2">
                <div className="h-8 w-8 rounded-full border-2 border-background bg-muted grid place-items-center text-xs">
                  {decision.primary_human_id?.slice(0, 2).toUpperCase() || '?'}
                </div>
              </div>
            </>
          ) : (
            <Badge variant="outline">Pending</Badge>
          )}
        </div>
      </div>
    </Link>
  )
}

