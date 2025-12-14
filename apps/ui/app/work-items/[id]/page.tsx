'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { WorkItemHeader } from '@/components/work-items/WorkItemHeader'
import { DecisionCard } from '@/components/work-items/DecisionCard'
import { ConstraintsTable } from '@/components/work-items/ConstraintsTable'
import { ActionsPanel } from '@/components/work-items/ActionsPanel'
import { OverrideModal } from '@/components/work-items/OverrideModal'
import { AuditDrawer } from '@/components/work-items/AuditDrawer'
import { useWorkItem, useDecision, useProfiles, useRecordOutcome } from '@/lib/queries'
import Link from 'next/link'

export default function WorkItemDetailPage() {
  const params = useParams()
  const router = useRouter()
  const workItemId = params.id as string

  const [overrideModalOpen, setOverrideModalOpen] = useState(false)
  const [auditDrawerOpen, setAuditDrawerOpen] = useState(false)

  const { data: workItem, isLoading: workItemLoading } = useWorkItem(workItemId)
  const { data: decision, isLoading: decisionLoading } = useDecision(workItemId)
  const { data: profilesData } = useProfiles(workItem?.service || '')
  const recordOutcome = useRecordOutcome()

  // Get assignee names from profiles
  const assigneeName = profilesData?.humans.find(
    (h) => h.human_id === decision?.primary_human_id
  )?.display_name

  const backupNames = decision?.backup_human_ids.map((id) =>
    profilesData?.humans.find((h) => h.human_id === id)?.display_name || id
  )

  const handleOverride = () => {
    setOverrideModalOpen(true)
  }

  const handleMarkResolved = async () => {
    if (!workItem || !decision) return

    const outcome = {
      event_id: `resolved-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      decision_id: decision.id,
      type: 'resolved',
      actor_id: 'user', // TODO: Get from auth
      timestamp: new Date().toISOString(),
    }

    try {
      await recordOutcome.mutateAsync({ workItemId: workItem.id, outcome })
      router.refresh()
    } catch (error) {
      console.error('Failed to mark resolved:', error)
    }
  }

  if (workItemLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12 text-muted-foreground">Loading work item...</div>
      </div>
    )
  }

  if (!workItem) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="text-red-500 mb-2">Work item not found</div>
          <Link href="/work-items">
            <Button variant="outline">Back to Work Items</Button>
                </Link>
                            </div>
                        </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Breadcrumb */}
      <nav className="text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground">Home</Link>
        {' > '}
        <Link href="/work-items" className="hover:text-foreground">Work Items</Link>
        {' > '}
        <span className="text-foreground">{workItem.id}</span>
      </nav>

      {/* Header */}
      <WorkItemHeader workItem={workItem} />

                {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Decision Card */}
        <div className="lg:col-span-2 space-y-6">
          {decisionLoading ? (
            <Card>
              <CardContent className="p-6">
                <div className="text-center text-muted-foreground">Loading decision...</div>
              </CardContent>
            </Card>
          ) : decision ? (
            <>
                    <DecisionCard
                decision={decision}
                assigneeName={assigneeName}
                backupNames={backupNames}
              />
              <ConstraintsTable constraints={decision.constraints_checked} />
            </>
          ) : (
            <Card>
              <CardContent className="p-6">
                <div className="text-center text-muted-foreground">
                  No decision made yet for this work item.
                </div>
              </CardContent>
            </Card>
          )}

          {/* Work Item Description */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-sm whitespace-pre-wrap">{workItem.description}</p>
            </CardContent>
          </Card>
                            </div>

        {/* Right Column - Actions */}
        <div className="space-y-6">
          <ActionsPanel
            workItem={workItem}
            hasDecision={!!decision}
            onOverride={handleOverride}
            onMarkResolved={handleMarkResolved}
          />

          {/* Audit Trail Button */}
          {decision && (
            <Button
              variant="outline"
              className="w-full"
              onClick={() => setAuditDrawerOpen(true)}
            >
              View Full Audit Trail
            </Button>
          )}
                </div>
            </div>

      {/* Modals */}
      {workItem && decision && (
            <OverrideModal
          isOpen={overrideModalOpen}
          onClose={() => setOverrideModalOpen(false)}
          workItemId={workItem.id}
          service={workItem.service}
          currentAssigneeId={decision.primary_human_id}
          currentAssigneeName={assigneeName}
        />
      )}

      <AuditDrawer
        isOpen={auditDrawerOpen}
        onClose={() => setAuditDrawerOpen(false)}
        workItemId={workItemId}
            />
        </div>
  )
}
