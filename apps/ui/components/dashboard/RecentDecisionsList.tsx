'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import { RecentDecisionItem } from './RecentDecisionItem'
import type { WorkItem } from '@/lib/types'

interface RecentDecisionsListProps {
  workItems: WorkItem[]
}

export function RecentDecisionsList({ workItems }: RecentDecisionsListProps) {
  return (
    <Card className="col-span-4">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Decisions</CardTitle>
        <Link href="/work-items">
          <Button variant="ghost" size="sm" className="text-primary hover:text-primary/80">
            View All <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {workItems.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No recent decisions
            </div>
          ) : (
            workItems.map((workItem) => (
              <RecentDecisionItem key={workItem.id} workItem={workItem} />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

