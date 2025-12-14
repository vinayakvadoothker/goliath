'use client'

import { useEffect, useMemo } from 'react'
import { DashboardStats } from '@/components/dashboard/DashboardStats'
import { RecentDecisionsList } from '@/components/dashboard/RecentDecisionsList'
import { ActiveIncidentsList } from '@/components/dashboard/ActiveIncidentsList'
import { SystemHealthPanel } from '@/components/dashboard/SystemHealthPanel'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { useWorkItems, useSystemHealth, useDecision } from '@/lib/queries'

export default function DashboardPage() {
  // Fetch all work items for stats
  const { data: workItemsData, isLoading: workItemsLoading } = useWorkItems({ limit: 1000 })
  
  // Fetch recent work items for decisions list
  const { data: recentWorkItemsData, isLoading: recentLoading } = useWorkItems({ limit: 5, offset: 0 })
  
  // System health
  const { data: healthData, isLoading: healthLoading } = useSystemHealth()

  // Calculate stats
  const stats = useMemo(() => {
    if (workItemsData) {
      const allWorkItems = workItemsData.work_items || []
      const total = workItemsData.total || 0
      const active = allWorkItems.filter(wi => !wi.jira_issue_key).length
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      const resolved7d = allWorkItems.filter(wi => 
        wi.jira_issue_key && new Date(wi.created_at) >= sevenDaysAgo
      ).length
      
      return {
        total,
        active,
        resolved7d,
        avgResolutionTime: '4.2h', // TODO: Calculate from outcomes
      }
    }
    return { total: 0, active: 0, resolved7d: 0, avgResolutionTime: 'N/A' }
  }, [workItemsData])

  // Recent work items
  const recentWorkItems = recentWorkItemsData?.work_items || []

  // Format health data
  const systemHealth = useMemo(() => {
    if (!healthData) return []
    return healthData.map(h => ({
      ...h,
      name: h.service,
    }))
  }, [healthData])

  const isLoading = workItemsLoading || recentLoading || healthLoading

  if (isLoading) {
    return (
      <div className="space-y-6 animate-in fade-in duration-500">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Mission control for work assignments.</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
          ))}
        </div>
        <div className="text-center py-12 text-muted-foreground">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Mission control for work assignments.</p>
        </div>
        <Link href="/work-items/new">
          <Button>Create Work Item</Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <DashboardStats {...stats} />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Recent Decisions */}
        <RecentDecisionsList workItems={recentWorkItems} />

        {/* System Status */}
        <SystemHealthPanel services={systemHealth} />
      </div>

      {/* Active Incidents */}
      <ActiveIncidentsList workItems={workItemsData?.work_items || []} />
    </div>
  )
}
