'use client'

import { StatCard } from './StatCard'

interface DashboardStatsProps {
  total: number
  active: number
  resolved7d: number
  avgResolutionTime: string
}

export function DashboardStats({ total, active, resolved7d, avgResolutionTime }: DashboardStatsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Total Work Items"
        value={total.toLocaleString()}
      />
      <StatCard
        label="Active Items"
        value={active.toString()}
        color="blue"
      />
      <StatCard
        label="Resolved (7d)"
        value={resolved7d.toString()}
        color="green"
      />
      <StatCard
        label="Avg Resolution"
        value={avgResolutionTime}
        unit="hours"
        color="purple"
      />
    </div>
  )
}

