'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Brain, Activity, Server, Zap, Database } from 'lucide-react'
import type { HealthCheck } from '@/lib/types'

interface ServiceStatus extends HealthCheck {
  name: string
}

const serviceIcons = {
  Ingest: Database,
  Decision: Brain,
  Learner: Activity,
  Executor: Server,
  Explain: Zap,
}

export function SystemHealthPanel({ services }: { services: ServiceStatus[] }) {
  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>System Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {services.map((service) => {
            const Icon = serviceIcons[service.name as keyof typeof serviceIcons] || Server
            const statusColor = service.healthy ? 'text-green-500' : 'text-red-500'

            return (
              <div key={service.name} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-md bg-secondary ${statusColor}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="font-medium">{service.name} Service</span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className={`h-2 w-2 rounded-full ${service.healthy ? 'bg-green-500' : 'bg-red-500'}`}
                  ></div>
                  <span className="text-sm text-muted-foreground">
                    {service.healthy ? 'Healthy' : 'Unhealthy'}
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-8 p-4 rounded-lg bg-secondary/50 border border-border">
          <h4 className="text-sm font-semibold mb-2">Wait Times</h4>
          <div className="flex justify-between items-end">
            <div className="text-center">
              <div className="text-2xl font-bold">12ms</div>
              <div className="text-xs text-muted-foreground">P99 Inference</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">45ms</div>
              <div className="text-xs text-muted-foreground">DB Latency</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">1.2s</div>
              <div className="text-xs text-muted-foreground">E2E Routing</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

