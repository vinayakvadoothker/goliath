'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertTriangle } from 'lucide-react'
import { useProfiles, useRecordOutcome } from '@/lib/queries'
import type { Candidate } from '@/lib/types'

interface OverrideModalProps {
  isOpen: boolean
  onClose: () => void
  workItemId: string
  service: string
  currentAssigneeId: string
  currentAssigneeName?: string
}

export function OverrideModal({
  isOpen,
  onClose,
  workItemId,
  service,
  currentAssigneeId,
  currentAssigneeName,
}: OverrideModalProps) {
  const [newAssigneeId, setNewAssigneeId] = useState<string>('')
  const [reason, setReason] = useState<string>('')
  
  const { data: profilesData, isLoading: profilesLoading } = useProfiles(service)
  const recordOutcome = useRecordOutcome()

  const availableHumans = profilesData?.humans || []

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newAssigneeId) return

    const outcome = {
      event_id: `override-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'reassigned',
      actor_id: 'user', // TODO: Get from auth
      timestamp: new Date().toISOString(),
      new_assignee_id: newAssigneeId,
    }

    try {
      await recordOutcome.mutateAsync({ workItemId, outcome })
      onClose()
      setNewAssigneeId('')
      setReason('')
    } catch (error) {
      console.error('Failed to override:', error)
    }
  }

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-background border-border">
                <DialogHeader>
          <DialogTitle>Override Assignment</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Reassign this work item to a different person. This will update the learning system.
                    </DialogDescription>
                </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Current Assignee */}
          <div>
            <Label>Current Assignee</Label>
            <div className="p-3 bg-muted rounded-md border mt-1">
              {currentAssigneeName || currentAssigneeId}
            </div>
          </div>

          {/* New Assignee */}
          <div>
            <Label>New Assignee</Label>
            {profilesLoading ? (
              <div className="p-3 bg-muted rounded-md border mt-1 text-sm text-muted-foreground">
                Loading...
              </div>
            ) : (
              <Select value={newAssigneeId} onValueChange={setNewAssigneeId}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select new assignee" />
                            </SelectTrigger>
                            <SelectContent>
                  {availableHumans
                    .filter((h: Candidate) => h.human_id !== currentAssigneeId)
                    .map((human: Candidate) => (
                      <SelectItem key={human.human_id} value={human.human_id}>
                        <div className="flex items-center justify-between w-full">
                          <span>{human.display_name}</span>
                          <span className="ml-4 text-xs text-muted-foreground">
                            Fit: {(human.fit_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                            </SelectContent>
                        </Select>
            )}
                    </div>

          {/* Reason */}
          <div>
            <Label>Reason (Optional)</Label>
                        <Textarea
              placeholder="Why are you overriding this assignment?"
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
              rows={3}
              className="mt-1"
                        />
                    </div>

          {/* Warning */}
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              This will decrease {currentAssigneeName || currentAssigneeId}'s fit_score and update the learning system.
            </AlertDescription>
          </Alert>

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={!newAssigneeId || recordOutcome.isPending}>
              {recordOutcome.isPending ? 'Reassigning...' : 'Reassign'}
            </Button>
                </div>
        </form>
            </DialogContent>
        </Dialog>
  )
}
