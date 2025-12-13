export interface LogEntry {
  id: string
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR'
  message: string
}

export interface Metric {
  name: string
  value: number
  unit?: string
  status: 'healthy' | 'warning' | 'error'
}

export interface Incident {
  id: string
  work_item_id: string
  error_type: string
  severity: 'sev1' | 'sev2' | 'sev3'
  error_message: string
  status: 'detected' | 'routing' | 'assigned' | 'resolved'
  assignee?: string
  jira_key?: string
  created_at: string
  decision_made_at?: string
  jira_created_at?: string
}

export interface Decision {
  work_item_id: string
  primary_human_id: string
  assignee_name: string
  confidence: number
  evidence: string[]
  constraints: ConstraintResult[]
  backup_human_ids: string[]
}

export interface ConstraintResult {
  name: string
  passed: boolean
  reason?: string
}

export interface SystemState {
  metrics: Metric[]
  logs: LogEntry[]
  incidents: Incident[]
  latest_decision?: Decision
}

export interface WebSocketMessage {
  type: 'incident_created' | 'decision_made' | 'jira_created' | 'log' | 'metric_update' | 'state_update'
  data: any
}

