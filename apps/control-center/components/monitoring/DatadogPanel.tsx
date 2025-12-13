"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LogStream } from "@/components/dashboard/LogStream"
import { MetricsPanel } from "@/components/dashboard/MetricsPanel"
import { IncidentTimeline } from "@/components/dashboard/IncidentTimeline"
import { SystemState } from "@/types"

interface DatadogPanelProps {
  state: SystemState
}

export function DatadogPanel({ state }: DatadogPanelProps) {
  // Convert metrics to Datadog format
  const metrics: Array<{name: string; value: number; unit?: string; status: 'healthy' | 'warning' | 'error'}> = [
    {
      name: "Requests/sec",
      value: (state.metrics as any)?.requests_per_sec || 0,
      status: ((state.metrics as any)?.requests_per_sec || 0) > 200 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "Error Rate",
      value: (state.metrics as any)?.error_rate || 0,
      unit: "/sec",
      status: ((state.metrics as any)?.error_rate || 0) > 10 ? 'error' as const : ((state.metrics as any)?.error_rate || 0) > 5 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "CPU Usage",
      value: (state.metrics as any)?.cpu_usage || 0,
      unit: "%",
      status: ((state.metrics as any)?.cpu_usage || 0) > 80 ? 'error' as const : ((state.metrics as any)?.cpu_usage || 0) > 60 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "Memory Usage",
      value: (state.metrics as any)?.memory_usage || 0,
      unit: "%",
      status: ((state.metrics as any)?.memory_usage || 0) > 85 ? 'error' as const : ((state.metrics as any)?.memory_usage || 0) > 70 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "Avg Latency",
      value: (state.metrics as any)?.avg_latency || 0,
      unit: "ms",
      status: ((state.metrics as any)?.avg_latency || 0) > 500 ? 'error' as const : ((state.metrics as any)?.avg_latency || 0) > 200 ? 'warning' as const : 'healthy' as const
    }
  ]

  const services = [
    { name: "API Service", status: ((state.metrics as any)?.error_rate || 0) > 10 ? 'error' : ((state.metrics as any)?.error_rate || 0) > 5 ? 'warning' : 'healthy' as const },
    { name: "Database", status: 'healthy' as const },
    { name: "Cache", status: 'healthy' as const }
  ]

  return (
    <div className="h-full flex flex-col">
      <Card className="flex-1 flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <span>Datadog Monitoring</span>
              <Badge variant="outline" className="text-xs">Simulated</Badge>
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden p-0">
          <Tabs defaultValue="metrics" className="h-full flex flex-col">
            <TabsList className="mx-6 mt-2">
              <TabsTrigger value="metrics">Metrics</TabsTrigger>
              <TabsTrigger value="logs">Logs</TabsTrigger>
              <TabsTrigger value="incidents">Incidents</TabsTrigger>
            </TabsList>
            <TabsContent value="metrics" className="flex-1 overflow-auto px-6 pb-6">
              <MetricsPanel metrics={metrics} />
            </TabsContent>
            <TabsContent value="logs" className="flex-1 overflow-hidden px-6 pb-6">
              <LogStream logs={state.logs || []} />
            </TabsContent>
            <TabsContent value="incidents" className="flex-1 overflow-auto px-6 pb-6">
              <IncidentTimeline incidents={state.incidents || []} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

