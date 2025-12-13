import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/StatCard";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Activity, Server, Brain } from "lucide-react";

export default function DashboardPage() {
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
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Work Items"
          value="1,234"
          trend="up"
          trendValue="+12%"
        />
        <StatCard
          label="Active Items"
          value="42"
        />
        <StatCard
          label="Resolved (7d)"
          value="156"
          trend="up"
          trendValue="+5%"
        />
        <StatCard
          label="Avg Resolution"
          value="4.2h"
          unit="hours"
          trend="down"
          trendValue="-0.5h"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Recent Decisions */}
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
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="h-9 w-9 bg-primary/20 text-primary rounded-full grid place-items-center font-bold text-xs">
                      WI
                    </div>
                    <div>
                      <div className="font-medium">API Latency Spike #{1200 + i}</div>
                      <div className="text-xs text-muted-foreground flex items-center gap-2">
                        <span>api-service</span>
                        <span>•</span>
                        <span>2 mins ago</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge variant="decision" className="bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 border-purple-500/20">
                      Auto-Assigned
                    </Badge>
                    <div className="flex -space-x-2">
                      <div className="h-8 w-8 rounded-full border-2 border-background bg-muted grid place-items-center text-xs">JD</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {[
                { name: "Decision Service", status: "Healthy", icon: Brain, color: "text-purple-500" },
                { name: "Learner Service", status: "Training", icon: Activity, color: "text-blue-500" },
                { name: "Executor Service", status: "Healthy", icon: Server, color: "text-green-500" },
              ].map((service) => (
                <div key={service.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-md bg-secondary ${service.color}`}>
                      <service.icon className="h-5 w-5" />
                    </div>
                    <span className="font-medium">{service.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${service.status === 'Healthy' ? 'bg-green-500' : 'bg-blue-500 animate-pulse'}`}></div>
                    <span className="text-sm text-muted-foreground">{service.status}</span>
                  </div>
                </div>
              ))}
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
      </div>
    </div>
  )
}
