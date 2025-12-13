// Goliath Shared TypeScript Types
// This is the single source of truth for all data structures

// Core entities
export interface WorkItem {
  id: string;
  type: 'incident' | 'ticket' | 'alert';
  service: string;
  severity: 'sev1' | 'sev2' | 'sev3' | 'sev4';
  description: string;
  created_at: string;
  origin_system: string;
  creator_id?: string;
  story_points?: number;  // For capacity matching (1-21, typically)
  impact?: 'high' | 'medium' | 'low';  // Impact level (separate from severity)
  raw_log?: string;  // Original raw log before preprocessing
  jira_issue_key?: string;  // If linked to Jira issue
}

export interface Human {
  id: string;
  display_name: string;
  contact_handles: {
    slack?: string;
    email?: string;
  };
  jira_account_id?: string; // For Jira API calls
  max_story_points?: number; // Max capacity for a sprint
  current_story_points?: number; // Currently assigned story points
  role?: string; // e.g., "backend-engineer", "sre"
}

export interface Decision {
  id: string;
  work_item_id: string;
  primary_human_id: string;
  backup_human_ids: string[];
  confidence: number; // 0-1
  constraints_checked: ConstraintResult[];
  created_at: string;
}

export interface ConstraintResult {
  name: string;
  passed: boolean;
  reason?: string;
}

export interface Evidence {
  type: 'recent_resolution' | 'recent_commit' | 'on_call' | 'low_load' | 'similar_incident';
  text: string;
  time_window: string;
  source: string;
}

export interface Outcome {
  event_id: string;
  decision_id: string;
  type: 'resolved' | 'reassigned' | 'escalated';
  actor_id: string;
  timestamp: string;
}

// Knowledge Graph Node Types
export type NodeType = 'human' | 'work_item' | 'service' | 'decision' | 'outcome';

export interface GraphNode {
  id: string;
  type: NodeType;
  name: string;
  x?: number;  // 3D coordinates
  y?: number;
  z?: number;
  size?: number;
  [key: string]: any;  // Additional properties
}

export interface GraphEdge {
  source: string;
  target: string;
  type: 'RESOLVED' | 'TRANSFERRED' | 'CO_WORKED' | 'TOUCHED';
  timestamp: string;
  width?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphEdge[];
}

