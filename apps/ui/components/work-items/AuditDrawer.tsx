'use client'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { useAudit } from '@/lib/queries'

interface AuditDrawerProps {
  isOpen: boolean
  onClose: () => void
  workItemId: string
}

export function AuditDrawer({ isOpen, onClose, workItemId }: AuditDrawerProps) {
  const { data: auditData, isLoading } = useAudit(workItemId)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] bg-background border-border">
        <DialogHeader>
          <DialogTitle>Audit Trail</DialogTitle>
          <DialogDescription>
            Complete decision reasoning chain for {workItemId}
          </DialogDescription>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh]">
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">Loading audit trail...</div>
          ) : auditData ? (
            <div className="space-y-6">
              {/* Decision Summary */}
              <div>
                <h3 className="font-semibold mb-2">Decision Summary</h3>
                <div className="p-4 bg-muted/50 rounded-lg space-y-2">
                  <div>
                    <span className="text-sm text-muted-foreground">Primary:</span>{' '}
                    <span className="font-medium">{auditData.decision.primary_human_id}</span>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Confidence:</span>{' '}
                    <span className="font-medium">{(auditData.decision.confidence * 100).toFixed(1)}%</span>
                  </div>
                  {auditData.decision.backup_human_ids.length > 0 && (
                    <div>
                      <span className="text-sm text-muted-foreground">Backups:</span>{' '}
                      <span className="font-medium">{auditData.decision.backup_human_ids.join(', ')}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* All Candidates */}
              <div>
                <h3 className="font-semibold mb-2">All Candidates</h3>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Fit Score</TableHead>
                        <TableHead>Resolves</TableHead>
                        <TableHead>Transfers</TableHead>
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
                            {candidate.filtered ? (
                              <Badge variant="outline" className="bg-red-500/20 text-red-400">
                                Filtered
                              </Badge>
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
              </div>

              {/* Constraints */}
              {auditData.constraints.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Constraints</h3>
                  <div className="space-y-2">
                    {auditData.constraints.map((constraint, idx) => (
                      <div key={idx} className="flex items-center gap-2 p-2 bg-muted/50 rounded">
                        <span className={constraint.passed ? 'text-green-500' : 'text-red-500'}>
                          {constraint.passed ? '✓' : '✗'}
                        </span>
                        <span className="font-mono text-sm">{constraint.name}</span>
                        {constraint.reason && (
                          <span className="text-sm text-muted-foreground">- {constraint.reason}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">No audit trail available</div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}

