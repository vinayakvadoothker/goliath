// API Client - All API functions

import type {
  WorkItemsResponse,
  WorkItem,
  Decision,
  AuditTrail,
  ProfilesResponse,
  HumanStats,
  HealthCheck,
  CreateWorkItemRequest,
  OutcomeRequest,
  GraphData,
} from './types'

// Base URLs
const INGEST_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
const DECISION_URL = process.env.NEXT_PUBLIC_DECISION_URL || 'http://localhost:8002'
const LEARNER_URL = process.env.NEXT_PUBLIC_LEARNER_URL || 'http://localhost:8003'
const EXECUTOR_URL = 'http://localhost:8004'
const EXPLAIN_URL = 'http://localhost:8005'

// Helper: Fetch with error handling
async function fetchAPI<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })
    
    if (!res.ok) {
      const errorText = await res.text()
      throw new Error(`API error (${res.status}): ${errorText}`)
    }
    
    return res.json()
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error(`Network error: ${String(error)}`)
  }
}

// Work Items API
export const workItemsAPI = {
  list: async (filters?: {
    service?: string
    severity?: string
    limit?: number
    offset?: number
  }): Promise<WorkItemsResponse> => {
    const params = new URLSearchParams()
    if (filters?.service) params.append('service', filters.service)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.limit) params.append('limit', filters.limit.toString())
    if (filters?.offset) params.append('offset', filters.offset.toString())
    
    return fetchAPI<WorkItemsResponse>(`${INGEST_URL}/work-items?${params}`)
  },

  get: async (id: string): Promise<WorkItem> => {
    return fetchAPI<WorkItem>(`${INGEST_URL}/work-items/${id}`)
  },

  create: async (data: CreateWorkItemRequest): Promise<WorkItem> => {
    return fetchAPI<WorkItem>(`${INGEST_URL}/work-items`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  recordOutcome: async (id: string, outcome: OutcomeRequest): Promise<{ outcome_id?: string; processed: boolean; message: string }> => {
    return fetchAPI(`${INGEST_URL}/work-items/${id}/outcome`, {
      method: 'POST',
      body: JSON.stringify(outcome),
    })
  },
}

// Decisions API
export const decisionsAPI = {
  get: async (workItemId: string): Promise<Decision> => {
    return fetchAPI<Decision>(`${DECISION_URL}/decisions/${workItemId}`)
  },

  getAudit: async (workItemId: string): Promise<AuditTrail> => {
    return fetchAPI<AuditTrail>(`${DECISION_URL}/audit/${workItemId}`)
  },
}

// Learner API
export const learnerAPI = {
  getProfiles: async (service: string): Promise<ProfilesResponse> => {
    return fetchAPI<ProfilesResponse>(`${LEARNER_URL}/profiles?service=${encodeURIComponent(service)}`)
  },

  getStats: async (humanId: string): Promise<HumanStats> => {
    return fetchAPI<HumanStats>(`${LEARNER_URL}/stats?human_id=${encodeURIComponent(humanId)}`)
  },
}

// Health Checks
export const healthAPI = {
  check: async (service: string, url: string): Promise<HealthCheck> => {
    try {
      const res = await fetch(`${url}/healthz`, {
        signal: AbortSignal.timeout(5000),
      })
      const data = await res.json()
      return {
        healthy: res.ok,
        service,
        status: data.status,
        url,
      }
    } catch {
      return {
        healthy: false,
        service,
        status: 'unreachable',
        url,
      }
    }
  },

  checkAll: async (): Promise<HealthCheck[]> => {
    return Promise.all([
      healthAPI.check('Ingest', INGEST_URL),
      healthAPI.check('Decision', DECISION_URL),
      healthAPI.check('Learner', LEARNER_URL),
      healthAPI.check('Executor', EXECUTOR_URL),
      healthAPI.check('Explain', EXPLAIN_URL),
    ])
  },
}

// Graph API
export const graphAPI = {
  get: async (filters?: {
    node_type?: string
    service?: string
    limit?: number
    time_start?: string
    time_end?: string
  }): Promise<GraphData> => {
    const params = new URLSearchParams()
    if (filters?.node_type) params.append('node_type', filters.node_type)
    if (filters?.service) params.append('service', filters.service)
    if (filters?.limit) params.append('limit', filters.limit.toString())
    if (filters?.time_start) params.append('time_start', filters.time_start)
    if (filters?.time_end) params.append('time_end', filters.time_end)
    
    return fetchAPI<GraphData>(`/api/graph?${params}`)
  },
}

