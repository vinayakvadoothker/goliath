'use client'

import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'
import { useStats } from '@/lib/queries'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'

export default function PersonDetailPage() {
  const params = useParams()
  const router = useRouter()
  const humanId = params.human_id as string

  const { data: statsData, isLoading } = useStats(humanId)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12 text-muted-foreground">Loading person stats...</div>
      </div>
    )
  }

  if (!statsData) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="text-red-500 mb-2">Person not found</div>
          <Link href="/people">
            <Button variant="outline">Back to People</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/people">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to People
            </Button>
          </Link>
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-lg">
                {statsData.display_name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">{statsData.display_name}</h1>
              <p className="text-muted-foreground">Human ID: {statsData.human_id}</p>
            </div>
          </div>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Service Stats</TabsTrigger>
          <TabsTrigger value="activity">Activity Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Load Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Current Load</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Pages (7 days)</span>
                  <span>{statsData.load.pages_7d}</span>
                </div>
                <Progress value={Math.min((statsData.load.pages_7d / 10) * 100, 100)} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Active Items</span>
                  <span>{statsData.load.active_items}</span>
                </div>
                <Progress value={Math.min((statsData.load.active_items / 5) * 100, 100)} />
              </div>
            </CardContent>
          </Card>

          {/* Service Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Service Capabilities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {statsData.services.map((service) => (
                  <div key={service.service} className="p-4 bg-muted/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{service.service}</span>
                      <Badge variant="outline">
                        {(service.fit_score * 100).toFixed(0)}%
                      </Badge>
                    </div>
                    <Progress value={service.fit_score * 100} className="mb-2" />
                    <div className="text-sm text-muted-foreground space-y-1">
                      <div>Resolves: {service.resolves_count}</div>
                      <div>Transfers: {service.transfers_count}</div>
                      {service.last_resolved_at && (
                        <div>
                          Last resolved:{' '}
                          {formatDistanceToNow(new Date(service.last_resolved_at), { addSuffix: true })}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          {statsData.services.map((service) => (
            <Card key={service.service}>
              <CardHeader>
                <CardTitle>{service.service}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Fit Score</span>
                    <span>{(service.fit_score * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={service.fit_score * 100} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Resolves</div>
                    <div className="text-2xl font-bold">{service.resolves_count}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Transfers</div>
                    <div className="text-2xl font-bold">{service.transfers_count}</div>
                  </div>
                </div>
                {service.last_resolved_at && (
                  <div className="text-sm text-muted-foreground">
                    Last resolved:{' '}
                    {formatDistanceToNow(new Date(service.last_resolved_at), { addSuffix: true })}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          {statsData.recent_outcomes && statsData.recent_outcomes.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {statsData.recent_outcomes.map((outcome) => (
                    <div
                      key={outcome.id}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                    >
                      <div>
                        <div className="font-medium">
                          {outcome.type === 'resolved' ? 'Resolved' : 'Reassigned'} work item
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {formatDistanceToNow(new Date(outcome.timestamp), { addSuffix: true })}
                        </div>
                      </div>
                      <Badge variant="outline">
                        {outcome.type}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-6">
                <div className="text-center text-muted-foreground">No recent activity</div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

