// React Query Hooks

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workItemsAPI, decisionsAPI, learnerAPI, healthAPI, graphAPI } from './api-client'
import type { CreateWorkItemRequest, OutcomeRequest } from './types'

// Work Items
export function useWorkItems(filters?: {
  service?: string
  severity?: string
  limit?: number
  offset?: number
}) {
  return useQuery({
    queryKey: ['work-items', filters],
    queryFn: () => workItemsAPI.list(filters),
    staleTime: 30000, // 30 seconds
  })
}

export function useWorkItem(id: string) {
  return useQuery({
    queryKey: ['work-item', id],
    queryFn: () => workItemsAPI.get(id),
    enabled: !!id,
  })
}

// Decisions
export function useDecision(workItemId: string) {
  return useQuery({
    queryKey: ['decision', workItemId],
    queryFn: () => decisionsAPI.get(workItemId),
    enabled: !!workItemId,
    retry: 1, // Don't retry if decision doesn't exist
  })
}

export function useAudit(workItemId: string) {
  return useQuery({
    queryKey: ['audit', workItemId],
    queryFn: () => decisionsAPI.getAudit(workItemId),
    enabled: !!workItemId,
  })
}

// Learner
export function useProfiles(service: string) {
  return useQuery({
    queryKey: ['profiles', service],
    queryFn: () => learnerAPI.getProfiles(service),
    enabled: !!service,
  })
}

export function useStats(humanId: string) {
  return useQuery({
    queryKey: ['stats', humanId],
    queryFn: () => learnerAPI.getStats(humanId),
    enabled: !!humanId,
  })
}

// Health Checks
export function useSystemHealth() {
  return useQuery({
    queryKey: ['system-health'],
    queryFn: () => healthAPI.checkAll(),
    refetchInterval: 30000, // Every 30 seconds
  })
}

// Mutations
export function useCreateWorkItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateWorkItemRequest) => workItemsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-items'] })
    },
  })
}

export function useRecordOutcome() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ workItemId, outcome }: { workItemId: string; outcome: OutcomeRequest }) =>
      workItemsAPI.recordOutcome(workItemId, outcome),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['work-items'] })
      queryClient.invalidateQueries({ queryKey: ['work-item', variables.workItemId] })
      queryClient.invalidateQueries({ queryKey: ['decision', variables.workItemId] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      queryClient.invalidateQueries({ queryKey: ['profiles'] })
      queryClient.invalidateQueries({ queryKey: ['graph'] })
    },
  })
}

// Graph
export function useGraph(filters?: {
  node_type?: string
  service?: string
  limit?: number
  time_start?: string
  time_end?: string
}) {
  return useQuery({
    queryKey: ['graph', filters],
    queryFn: () => graphAPI.get(filters),
    staleTime: 60000, // 1 minute
  })
}

