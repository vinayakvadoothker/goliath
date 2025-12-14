'use client'

import { useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useAudit } from '@/lib/queries'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

export default function DecisionDetailPage() {
  const params = useParams()
  const workItemId = params.work_item_id as string

  const { data: auditData, isLoading } = useAudit(workItemId)

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12 text-muted-foreground">Loading audit trail...</div>
      </div>
    )
  }

  if (!auditData) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="text-red-500 mb-2">Audit trail not found</div>
          <Link href="/work-items">
            <Button variant="outline">Back to Work Items</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link href={`/work-items/${workItemId}`}>
            <Button variant="ghost" size="sm" className="mb-2">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Work Item
            </Button>
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">Decision Audit Trail</h1>
          <p className="text-muted-foreground">Complete decision reasoning for {workItemId}</p>
        </div>
      </div>

      {/* Decision Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Decision Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-muted-foreground mb-1">Primary Assignee</div>
              <div className="font-semibold">{auditData.decision.primary_human_id}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground mb-1">Confidence</div>
              <div className="flex items-center gap-2">
                <Progress value={auditData.decision.confidence * 100} className="flex-1" />
                <span className="font-semibold">{(auditData.decision.confidence * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
          {auditData.decision.backup_human_ids.length > 0 && (
            <div>
              <div className="text-sm text-muted-foreground mb-1">Backup Assignees</div>
              <div className="flex gap-2">
                {auditData.decision.backup_human_ids.map((id) => (
                  <Badge key={id} variant="outline">
                    {id}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* All Candidates */}
      <Card>
        <CardHeader>
          <CardTitle>All Candidates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Fit Score</TableHead>
                  <TableHead>Resolves</TableHead>
                  <TableHead>Transfers</TableHead>
                  <TableHead>On Call</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auditData.candidates.map((candidate) => (
                  <TableRow key={candidate.human_id}>
                    <TableCell className="font-medium">
                      {candidate.display_name}
                      {candidate.human_id === auditData.decision.primary_human_id && (
                        <Badge variant="outline" className="ml-2 bg-purple-500/20">
                          Primary
                        </Badge>
                      )}
                      {auditData.decision.backup_human_ids.includes(candidate.human_id) && (
                        <Badge variant="outline" className="ml-2">
                          Backup
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{(candidate.fit_score * 100).toFixed(1)}%</TableCell>
                    <TableCell>{candidate.resolves_count}</TableCell>
                    <TableCell>{candidate.transfers_count}</TableCell>
                    <TableCell>
                      {candidate.on_call ? (
                        <Badge variant="outline" className="bg-green-500/20 text-green-400">
                          Yes
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">No</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {candidate.filtered ? (
                        <div>
                          <Badge variant="outline" className="bg-red-500/20 text-red-400">
                            Filtered
                          </Badge>
                          {candidate.filter_reason && (
                            <div className="text-xs text-muted-foreground mt-1">
                              {candidate.filter_reason}
                            </div>
                          )}
                        </div>
                      ) : (
                        <Badge variant="outline" className="bg-green-500/20 text-green-400">
                          Considered
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Constraints */}
      {auditData.constraints.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Constraints Checked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {auditData.constraints.map((constraint, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg"
                >
                  <span className={constraint.passed ? 'text-green-500 text-xl' : 'text-red-500 text-xl'}>
                    {constraint.passed ? '✓' : '✗'}
                  </span>
                  <div className="flex-1">
                    <div className="font-mono text-sm font-semibold">{constraint.name}</div>
                    {constraint.reason && (
                      <div className="text-sm text-muted-foreground mt-1">{constraint.reason}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

