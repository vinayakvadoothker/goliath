// API Response Types

export interface WorkItem {
  id: string
  type: string
  service: string
  severity: string
  description: string
  created_at: string
  origin_system: string
  jira_issue_key?: string
  story_points?: number
  impact?: string
  raw_log?: string
  creator_id?: string
}

export interface WorkItemsResponse {
  work_items: WorkItem[]
  total: number
  limit: number
  offset: number
}

export interface ConstraintResult {
  name: string
  passed: boolean
  reason?: string
}

export interface Decision {
  id: string
  work_item_id: string
  primary_human_id: string
  backup_human_ids: string[]
  confidence: number
  constraints_checked: ConstraintResult[]
  created_at: string
}

export interface Candidate {
  human_id: string
  display_name: string
  fit_score: number
  resolves_count: number
  transfers_count: number
  last_resolved_at?: string
  on_call: boolean
  pages_7d: number
  active_items: number
  max_story_points?: number
  current_story_points?: number
  resolved_by_severity?: {
    sev1: number
    sev2: number
    sev3: number
    sev4: number
  }
  filtered?: boolean
  filter_reason?: string
  score_breakdown?: ScoreBreakdown
}

export interface ScoreBreakdown {
  fit_score?: number
  vector_similarity?: number
  capacity?: number
  severity_match?: number
  [key: string]: number | undefined
}

export interface AuditTrail {
  work_item_id: string
  decision_id: string
  decision: {
    primary_human_id: string
    backup_human_ids: string[]
    confidence: number
    created_at: string
  }
  candidates: Candidate[]
  constraints: ConstraintResult[]
}

export interface ProfilesResponse {
  service: string
  humans: Candidate[]
}

export interface ServiceStats {
  service: string
  fit_score: number
  resolves_count: number
  transfers_count: number
  last_resolved_at?: string
}

export interface Load {
  pages_7d: number
  active_items: number
}

export interface Outcome {
  id: string
  work_item_id: string
  type: string
  actor_id: string
  timestamp: string
  service: string
}

export interface HumanStats {
  human_id: string
  display_name: string
  services: ServiceStats[]
  load: Load
  recent_outcomes?: Outcome[]
}

export interface HealthCheck {
  healthy: boolean
  service: string
  status?: string
  url?: string
}

export interface CreateWorkItemRequest {
  type: string
  service: string
  severity: string
  description: string
  origin_system: string
  creator_id?: string
  raw_log?: string
}

export interface OutcomeRequest {
  event_id: string
  decision_id?: string
  type: string
  actor_id: string
  timestamp: string
  new_assignee_id?: string
}

// Graph types
export type GraphNodeType = 'human' | 'work_item' | 'service' | 'decision' | 'outcome'

export interface GraphNode {
  id: string
  type: GraphNodeType
  name: string
  label: string
  x: number
  y: number
  z: number
  color: string
  val: number
  group: string
  metadata?: Record<string, any>
}

export interface GraphEdge {
  source: string
  target: string
  type: 'RESOLVED' | 'TRANSFERRED' | 'CO_WORKED' | 'ASSIGNED'
  timestamp: string
  weight?: number
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphEdge[]
  stats: {
    total_nodes: number
    total_edges: number
    by_type: {
      human: number
      work_item: number
      service: number
      decision: number
      outcome: number
    }
  }
}

