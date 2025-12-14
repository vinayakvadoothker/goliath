# UI Redesign - Complete Implementation Guide

**Complete redesign of the UI application using real APIs - no hardcoded data.**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Application Structure](#application-structure)
3. [API Integration](#api-integration)
4. [Page-by-Page Implementation](#page-by-page-implementation)
5. [Component Architecture](#component-architecture)
6. [State Management](#state-management)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Implementation Checklists](#implementation-checklists)
9. [Testing Strategy](#testing-strategy)

---

## Architecture Overview

### Design Principles

1. **No Hardcoded Data** - Everything comes from APIs
2. **Real-time Updates** - Polling or WebSocket for live data
3. **Evidence-First** - Every decision shows why it was made
4. **Full Audit Trail** - Complete transparency on routing decisions
5. **Learning Loop Integration** - Override workflow updates system

### Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **3D Visualization**: react-force-graph-3d
- **Date Formatting**: date-fns

---

## Application Structure

```
apps/ui/
├── app/
│   ├── layout.tsx                    # Root layout (Navbar + Sidebar)
│   ├── page.tsx                      # Landing page (existing)
│   ├── dashboard/
│   │   └── page.tsx                  # Main dashboard
│   ├── work-items/
│   │   ├── page.tsx                  # Work items list
│   │   ├── [id]/
│   │   │   └── page.tsx              # Work item detail
│   │   └── new/
│   │       └── page.tsx              # Create new work item
│   ├── decisions/
│   │   ├── page.tsx                  # All decisions list
│   │   └── [work_item_id]/
│   │       └── page.tsx              # Decision detail + audit
│   ├── people/
│   │   ├── page.tsx                  # People list
│   │   └── [human_id]/
│   │       └── page.tsx              # Person stats & profile
│   ├── graph/
│   │   └── page.tsx                  # 3D knowledge graph
│   └── api/
│       └── proxy/                    # Next.js API routes (optional)
│           ├── work-items/
│           ├── decisions/
│           └── stats/
├── components/
│   ├── layout/                       # Layout components
│   ├── dashboard/                    # Dashboard components
│   ├── work-items/                   # Work items components
│   ├── decisions/                     # Decisions components
│   ├── people/                       # People components
│   ├── graph/                        # Graph components
│   └── ui/                           # shadcn/ui components
├── lib/
│   ├── api-client.ts                 # API client functions
│   ├── queries.ts                    # React Query hooks
│   ├── types.ts                      # TypeScript types
│   └── utils.ts                      # Utility functions
└── hooks/
    └── use-system-updates.ts         # Real-time updates hook
```

---

## API Integration

### Base URLs

```typescript
// Environment variables (from next.config.js)
const INGEST_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
const DECISION_URL = process.env.NEXT_PUBLIC_DECISION_URL || 'http://localhost:8002'
const LEARNER_URL = process.env.NEXT_PUBLIC_LEARNER_URL || 'http://localhost:8003'
const EXECUTOR_URL = 'http://localhost:8004'
const EXPLAIN_URL = 'http://localhost:8005'
```

### API Endpoints Used

#### Ingest Service (Port 8001)

| Endpoint | Method | Purpose | Used In |
|----------|--------|---------|---------|
| `/work-items` | GET | List work items | Dashboard, Work Items List |
| `/work-items/{id}` | GET | Get work item | Work Item Detail |
| `/work-items` | POST | Create work item | Create Work Item Page |
| `/work-items/{id}/outcome` | POST | Record outcome | Override Modal, Mark Resolved |
| `/healthz` | GET | Health check | Dashboard System Status |

#### Decision Service (Port 8002)

| Endpoint | Method | Purpose | Used In |
|----------|--------|---------|---------|
| `/decisions/{work_item_id}` | GET | Get decision | Work Item Detail, Decision Detail |
| `/audit/{work_item_id}` | GET | Get audit trail | Decision Detail, Audit Drawer |
| `/healthz` | GET | Health check | Dashboard System Status |

#### Learner Service (Port 8003)

| Endpoint | Method | Purpose | Used In |
|----------|--------|---------|---------|
| `/profiles?service={service}` | GET | Get human profiles | Decision Detail, Override Modal |
| `/stats?human_id={id}` | GET | Get human stats | Person Detail Page |
| `/healthz` | GET | Health check | Dashboard System Status |

#### Executor Service (Port 8004)

| Endpoint | Method | Purpose | Used In |
|----------|--------|---------|---------|
| `/healthz` | GET | Health check | Dashboard System Status |

#### Explain Service (Port 8005)

| Endpoint | Method | Purpose | Used In |
|----------|--------|---------|---------|
| `/healthz` | GET | Health check | Dashboard System Status |

---

## Page-by-Page Implementation

### 1. Dashboard (`/dashboard`)

**Purpose**: System overview with real-time stats and recent activity

**Data Sources**:
- Work Items API (for stats)
- Decisions API (for recent decisions)
- Health checks (for system status)

**API Calls**:
```typescript
// On page load (parallel):
1. GET /work-items?limit=1000
   → Calculate: total, active, resolved (7d)

2. GET /work-items?limit=5&offset=0
   → For each: GET /decisions/{work_item_id}
   → Combine work item + decision data

3. Health checks (parallel):
   - GET http://localhost:8001/healthz
   - GET http://localhost:8002/healthz
   - GET http://localhost:8003/healthz
   - GET http://localhost:8004/healthz
   - GET http://localhost:8005/healthz
```

**Components**:
- `DashboardStats` - 4 stat cards
- `RecentDecisionsList` - Last 5 decisions
- `ActiveIncidentsList` - Active work items (no jira_issue_key)
- `SystemHealthPanel` - Service health status

**Stats Calculation**:
```typescript
// Total Work Items
total = response.total

// Active Items (not yet executed)
active = workItems.filter(wi => !wi.jira_issue_key).length

// Resolved (7 days)
const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
resolved7d = workItems.filter(wi => 
  wi.jira_issue_key && new Date(wi.created_at) >= sevenDaysAgo
).length

// Avg Resolution Time (TODO: Calculate from outcomes or jira_issues)
avgResolutionTime = "4.2h" // Placeholder until outcomes API available
```

**Real-time Updates**: Poll every 30 seconds

---

### 2. Work Items List (`/work-items`)

**Purpose**: Browse all work items with filtering and pagination

**Data Sources**:
- Work Items API

**API Calls**:
```typescript
// Initial load:
GET /work-items?limit=50&offset=0

// Filter by service:
GET /work-items?service=api-service&limit=50&offset=0

// Filter by severity:
GET /work-items?severity=sev1&limit=50&offset=0

// Pagination:
GET /work-items?limit=50&offset=50
```

**Components**:
- `WorkItemsTable` - Data table
- `WorkItemsFilters` - Service, Severity, Search
- `WorkItemsPagination` - Previous/Next

**Table Columns**:
- ID (link to detail)
- Service
- Severity (badge)
- Created (formatted date)
- Status (open/assigned/resolved)
- Assignee (from decision)
- Actions (View button)

**User Actions**:
- Click row → Navigate to `/work-items/[id]`
- Filter change → Refetch with new params
- Search → Client-side filter (or add search param to API)

---

### 3. Work Item Detail (`/work-items/[id]`)

**Purpose**: View work item details, decision, and take actions

**Data Sources**:
- Work Items API
- Decisions API
- Learner API (for assignee names)

**API Calls**:
```typescript
// On page load (parallel):
1. GET /work-items/{id}
2. GET /decisions/{id}
   → If decision exists:
      - GET /audit/{id} (optional, lazy load)
      - GET /profiles?service={work_item.service} (for assignee names)
```

**Components**:
- `WorkItemHeader` - Service, Severity, Created, Status badges
- `DecisionCard` - Primary assignee, backups, confidence, evidence
- `ConstraintsTable` - Constraint name, passed/failed, reason
- `ActionsPanel` - Override, Mark Resolved, View in Jira, View Audit
- `AuditDrawer` - Slide-out panel with full audit trail

**User Actions**:

1. **Override Assignment**:
   ```typescript
   // Opens OverrideModal
   // User selects new assignee
   POST /work-items/{id}/outcome
   {
     event_id: uuid(),
     type: "reassigned",
     actor_id: current_user_id,
     new_assignee_id: selected_human_id,
     timestamp: now(),
     decision_id: decision.id
   }
   // Refresh page to show new assignee
   ```

2. **Mark Resolved**:
   ```typescript
   POST /work-items/{id}/outcome
   {
     event_id: uuid(),
     type: "resolved",
     actor_id: current_user_id,
     timestamp: now(),
     decision_id: decision.id
   }
   ```

3. **View Audit Trail**:
   ```typescript
   // Opens drawer
   GET /audit/{id}
   // Shows: all candidates, scores, filter reasons
   ```

4. **View in Jira**:
   ```typescript
   // External link
   window.open(`https://jira.example.com/browse/${workItem.jira_issue_key}`)
   ```

---

### 4. Decision Detail (`/decisions/[work_item_id]`)

**Purpose**: Full audit trail of routing decision

**Data Sources**:
- Decisions API (audit endpoint)

**API Calls**:
```typescript
// On page load:
GET /audit/{work_item_id}
// Returns:
// - Decision details
// - All candidates with scores
// - Filter reasons
// - Constraints
// - Score breakdowns
```

**Components**:
- `DecisionHeader` - Primary assignee, confidence badge
- `CandidatesTable` - All candidates with:
  - Display name
  - Fit score
  - Resolves count
  - Transfers count
  - Filter reason (if filtered)
  - Score breakdown (expandable)
- `ConstraintsList` - All constraints with pass/fail
- `ScoreBreakdownChart` - Visual breakdown of scoring

**Display Logic**:
- Show all candidates (not just top 3)
- Highlight primary and backups
- Show why each candidate was filtered (if applicable)
- Expandable score breakdown per candidate

---

### 5. People List (`/people`)

**Purpose**: Browse all humans in the system

**Data Sources**:
- Learner API (stats endpoint)

**API Calls**:
```typescript
// Get all humans (would need new endpoint or query database)
// For now: Get from all services
GET /profiles?service=api-service
GET /profiles?service=payment-service
// ... etc
// Combine and deduplicate humans
```

**Components**:
- `PeopleTable` - List of humans
- `PeopleFilters` - Filter by service

**Table Columns**:
- Name
- Services (badges)
- Overall Fit Score (weighted average)
- Total Resolves
- Total Transfers
- Actions (View Profile)

**User Actions**:
- Click row → Navigate to `/people/[human_id]`

---

### 6. Person Detail (`/people/[human_id]`)

**Purpose**: View person stats and capabilities

**Data Sources**:
- Learner API (stats endpoint)

**API Calls**:
```typescript
// On page load:
GET /stats?human_id={human_id}
// Returns:
// - All service stats
// - Load data (pages_7d, active_items)
// - Recent outcomes
```

**Components**:
- `PersonHeader` - Name, avatar, contact info
- `ServiceStatsGrid` - Cards for each service:
  - Fit score (progress bar)
  - Resolves count
  - Transfers count
  - Last resolved date
  - Resolved by severity breakdown
- `LoadMetrics` - Pages 7d, active items
- `ActivityTimeline` - Recent outcomes (resolved/reassigned)

**Tabs**:
- Overview (summary stats)
- Service Stats (per-service breakdown)
- Activity Timeline (chronological outcomes)

---

### 7. Create Work Item (`/work-items/new`)

**Purpose**: Manually create a new work item

**Data Sources**:
- Work Items API (POST)

**API Calls**:
```typescript
// On form submit:
POST /work-items
{
  type: "incident",
  service: selected_service,
  severity: selected_severity,
  description: description,
  origin_system: "ui",
  creator_id: current_user_id
}
// This triggers automatic orchestration:
// - Decision Service
// - Explain Service
// - Executor Service
// Redirect to /work-items/{new_id}
```

**Components**:
- `CreateWorkItemForm` - Form with validation
- `ServiceSelect` - Dropdown of available services
- `SeveritySelect` - sev1, sev2, sev3, sev4

**Form Fields**:
- Service (required, dropdown)
- Severity (required, dropdown)
- Description (required, textarea)
- Type (optional, default: "incident")

---

### 8. Knowledge Graph (`/graph`)

**Purpose**: 3D interactive visualization of knowledge graph

**Data Sources**:
- PostgreSQL (direct query or new API endpoint)

**API Calls**:
```typescript
// Option 1: Create new endpoint GET /graph/nodes
// Option 2: Query database directly via Next.js API route

// Get nodes:
SELECT 
  id, 'work_item' as type, description as name,
  embedding_3d_x, embedding_3d_y, embedding_3d_z
FROM work_items
UNION
SELECT 
  id, 'human' as type, display_name as name,
  NULL, NULL, NULL
FROM humans
UNION
SELECT 
  id, 'decision' as type, id as name,
  NULL, NULL, NULL
FROM decisions

// Get edges (from outcomes table):
SELECT 
  work_item_id as source_id,
  actor_id as target_id,
  'RESOLVED' as edge_type,
  timestamp
FROM outcomes
WHERE type = 'resolved'
UNION
SELECT 
  work_item_id as source_id,
  new_assignee_id as target_id,
  'TRANSFERRED' as edge_type,
  timestamp
FROM outcomes
WHERE type = 'reassigned'
```

**Components**:
- `KnowledgeGraph3D` - react-force-graph-3d component
- `GraphFilters` - Node type, service, time range dropdowns
- `NodeDetailsPanel` - Sidebar showing node details when clicked
- `GraphLegend` - Color coding reference

**Node Colors**:
- Humans: Blue (#3b82f6)
- Work Items: Red (#ef4444)
- Services: Green (#10b981)
- Decisions: Purple (#8b5cf6)
- Outcomes: Amber (#f59e0b)

**Interactions**:
- Drag to rotate
- Scroll to zoom
- Click node → Show details in sidebar
- Hover node → Highlight connected nodes
- Filter by node type, service, time range

---

## Component Architecture

### Layout Components

#### `Navbar.tsx`
- Logo/Brand
- Navigation links (Dashboard, Work Items, People, Graph)
- User menu (if needed)

#### `Sidebar.tsx`
- Navigation menu
- Quick filters (Service, Severity)
- Recent work items (last 5, clickable)
- Collapsible

#### `MainLayout.tsx`
- Wrapper with Navbar + Sidebar
- Applies to all pages except landing

---

### Dashboard Components

#### `DashboardStats.tsx`
- 4 stat cards in grid
- Props: `{ total, active, resolved7d, avgResolutionTime }`
- Shows trends (up/down arrows)

#### `RecentDecisionsList.tsx`
- List of last 5 decisions
- Props: `{ decisions: Array<{ workItem, decision }> }`
- Each item: Work item info + assignee + link to detail

#### `ActiveIncidentsList.tsx`
- List of work items without jira_issue_key
- Props: `{ workItems: WorkItem[] }`
- Shows: Service, Severity, Created, Status

#### `SystemHealthPanel.tsx`
- Service health status
- Props: `{ services: Array<{ name, healthy, status }> }`
- Shows: Icon, name, health indicator

---

### Work Items Components

#### `WorkItemsTable.tsx`
- Data table with sorting
- Props: `{ workItems: WorkItem[], onRowClick: (id) => void }`
- Columns: ID, Service, Severity, Created, Status, Assignee, Actions

#### `WorkItemsFilters.tsx`
- Filter controls
- Props: `{ onFilterChange: (filters) => void }`
- Filters: Service dropdown, Severity dropdown, Search input

#### `WorkItemDetail.tsx`
- Main detail view
- Props: `{ workItemId: string }`
- Fetches: Work item, Decision, Audit (lazy)

#### `DecisionCard.tsx`
- Decision display
- Props: `{ decision: Decision, assigneeName: string }`
- Shows: Primary assignee, backups, confidence, evidence

#### `ConstraintsTable.tsx`
- Constraints list
- Props: `{ constraints: ConstraintResult[] }`
- Shows: Name, Pass/Fail icon, Reason

#### `OverrideModal.tsx`
- Override form dialog
- Props: `{ isOpen, onClose, workItemId, currentAssigneeId }`
- Fetches: Available humans from `/profiles?service={service}`
- Submits: `POST /work-items/{id}/outcome`

#### `AuditDrawer.tsx`
- Slide-out audit panel
- Props: `{ isOpen, onClose, workItemId }`
- Fetches: `GET /audit/{work_item_id}`
- Shows: All candidates, scores, filter reasons

---

### Decisions Components

#### `DecisionsList.tsx`
- List of all decisions
- Props: `{ decisions: Decision[] }`
- Shows: Work item, Assignee, Confidence, Created

#### `DecisionDetail.tsx`
- Full decision view
- Props: `{ workItemId: string }`
- Fetches: `GET /audit/{work_item_id}`

#### `CandidatesTable.tsx`
- All candidates with scores
- Props: `{ candidates: Candidate[] }`
- Columns: Name, Fit Score, Resolves, Transfers, Filter Reason, Score Breakdown

#### `ScoreBreakdownChart.tsx`
- Visual score breakdown
- Props: `{ breakdown: ScoreBreakdown }`
- Shows: Bar chart of fit_score, vector_similarity, capacity, etc.

---

### People Components

#### `PeopleList.tsx`
- List of all humans
- Props: `{ people: Human[] }`
- Shows: Name, Services, Overall Fit Score, Stats

#### `PersonProfile.tsx`
- Person header
- Props: `{ human: Human }`
- Shows: Name, avatar, contact info

#### `ServiceStatsGrid.tsx`
- Per-service stats cards
- Props: `{ stats: ServiceStats[] }`
- Each card: Service name, Fit score, Resolves, Transfers, Last resolved

#### `LoadMetrics.tsx`
- Current load display
- Props: `{ load: { pages_7d, active_items } }`
- Shows: Metrics with progress bars

#### `ActivityTimeline.tsx`
- Recent outcomes timeline
- Props: `{ outcomes: Outcome[] }`
- Shows: Chronological list of resolved/reassigned

---

### Graph Components

#### `KnowledgeGraph3D.tsx`
- 3D graph component
- Props: `{ nodes: Node[], links: Link[] }`
- Uses: react-force-graph-3d

#### `GraphFilters.tsx`
- Filter controls
- Props: `{ onFilterChange: (filters) => void }`
- Filters: Node type, Service, Time range

#### `NodeDetailsPanel.tsx`
- Node info sidebar
- Props: `{ node: Node | null }`
- Shows: Node type, name, details (depends on type)

#### `GraphLegend.tsx`
- Color coding reference
- Props: `{ nodeCounts: Record<string, number> }`
- Shows: Node type, color, count

---

## State Management

### React Query Setup

**Install**:
```bash
npm install @tanstack/react-query
```

**Provider Setup** (`app/layout.tsx`):
```typescript
'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      refetchOnWindowFocus: false,
    },
  },
})

export default function RootLayout({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

### Query Hooks (`lib/queries.ts`)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workItemsAPI, decisionsAPI, learnerAPI } from './api-client'

// Work Items
export function useWorkItems(filters?: any) {
  return useQuery({
    queryKey: ['work-items', filters],
    queryFn: () => workItemsAPI.list(filters),
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

// Mutations
export function useCreateWorkItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => workItemsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['work-items'] })
    },
  })
}

export function useRecordOutcome() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ workItemId, outcome }: any) => 
      workItemsAPI.recordOutcome(workItemId, outcome),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['work-items'] })
      queryClient.invalidateQueries({ queryKey: ['decision', variables.workItemId] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
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
```

---

## Data Flow Diagrams

### Dashboard Load Flow

```
User visits /dashboard
    ↓
useSystemHealth() → Health checks (parallel)
    ↓
useWorkItems({ limit: 1000 }) → GET /work-items
    ↓
Calculate stats (total, active, resolved7d)
    ↓
useWorkItems({ limit: 5 }) → GET /work-items?limit=5
    ↓
For each work item:
    useDecision(workItemId) → GET /decisions/{id}
    ↓
Combine work item + decision data
    ↓
Render DashboardStats + RecentDecisionsList + SystemHealthPanel
```

### Override Flow

```
User clicks "Override" on Work Item Detail
    ↓
OverrideModal opens
    ↓
useProfiles(service) → GET /profiles?service={service}
    ↓
Show dropdown with all humans + fit_score
    ↓
User selects new assignee + submits
    ↓
useRecordOutcome().mutate({
  workItemId,
  outcome: {
    event_id: uuid(),
    type: "reassigned",
    new_assignee_id: selectedId,
    ...
  }
})
    ↓
POST /work-items/{id}/outcome
    ↓
Learner Service updates fit_scores
    ↓
React Query invalidates queries
    ↓
Page refreshes → Shows new assignee
```

### Work Item Creation Flow

```
User fills form on /work-items/new
    ↓
User submits
    ↓
useCreateWorkItem().mutate(formData)
    ↓
POST /work-items
    ↓
Ingest Service creates work item
    ↓
Auto-orchestration triggers:
    ├── Decision Service → Makes decision
    ├── Explain Service → Generates evidence
    └── Executor Service → Creates Jira issue
    ↓
Redirect to /work-items/{new_id}
    ↓
Page loads → Shows work item + decision
```

---

## Implementation Checklists

### Phase 1: Foundation

#### Setup & Configuration
- [ ] Install React Query: `npm install @tanstack/react-query`
- [ ] Install date-fns: `npm install date-fns`
- [ ] Create `lib/api-client.ts` with all API functions
- [ ] Create `lib/queries.ts` with React Query hooks
- [ ] Create `lib/types.ts` with TypeScript interfaces
- [ ] Setup QueryClientProvider in `app/layout.tsx`
- [ ] Verify environment variables in `next.config.js`

#### API Client Implementation
- [ ] Implement `workItemsAPI.list()` - GET /work-items
- [ ] Implement `workItemsAPI.get()` - GET /work-items/{id}
- [ ] Implement `workItemsAPI.create()` - POST /work-items
- [ ] Implement `workItemsAPI.recordOutcome()` - POST /work-items/{id}/outcome
- [ ] Implement `decisionsAPI.get()` - GET /decisions/{id}
- [ ] Implement `decisionsAPI.getAudit()` - GET /audit/{id}
- [ ] Implement `learnerAPI.getProfiles()` - GET /profiles?service={service}
- [ ] Implement `learnerAPI.getStats()` - GET /stats?human_id={id}
- [ ] Implement `healthAPI.checkAll()` - Health checks for all services
- [ ] Add error handling to all API functions
- [ ] Add TypeScript types for all API responses

#### React Query Hooks
- [ ] Create `useWorkItems()` hook
- [ ] Create `useWorkItem()` hook
- [ ] Create `useDecision()` hook
- [ ] Create `useAudit()` hook
- [ ] Create `useProfiles()` hook
- [ ] Create `useStats()` hook
- [ ] Create `useCreateWorkItem()` mutation
- [ ] Create `useRecordOutcome()` mutation
- [ ] Create `useSystemHealth()` hook
- [ ] Test all hooks with real API calls

---

### Phase 2: Dashboard

#### Dashboard Page
- [ ] Create `app/dashboard/page.tsx` (client component)
- [ ] Implement stats calculation (total, active, resolved7d)
- [ ] Fetch recent work items
- [ ] Fetch decisions for recent work items
- [ ] Fetch system health
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add polling (refresh every 30 seconds)

#### Dashboard Components
- [ ] Create `components/dashboard/DashboardStats.tsx`
- [ ] Create `components/dashboard/RecentDecisionsList.tsx`
- [ ] Create `components/dashboard/ActiveIncidentsList.tsx`
- [ ] Create `components/dashboard/SystemHealthPanel.tsx`
- [ ] Style all components with Tailwind
- [ ] Add loading skeletons
- [ ] Add empty states

#### Testing
- [ ] Test dashboard with real data
- [ ] Test with no work items (empty state)
- [ ] Test with API errors (error state)
- [ ] Test polling refresh
- [ ] Test health check failures

---

### Phase 3: Work Items

#### Work Items List Page
- [ ] Create `app/work-items/page.tsx` (client component)
- [ ] Implement table with columns
- [ ] Implement filtering (service, severity)
- [ ] Implement search (client-side or API)
- [ ] Implement pagination
- [ ] Add loading states
- [ ] Add error handling
- [ ] Link rows to detail page

#### Work Items Components
- [ ] Create `components/work-items/WorkItemsTable.tsx`
- [ ] Create `components/work-items/WorkItemsFilters.tsx`
- [ ] Create `components/work-items/WorkItemsPagination.tsx`
- [ ] Style all components
- [ ] Add loading states
- [ ] Add empty states

#### Work Item Detail Page
- [ ] Create `app/work-items/[id]/page.tsx` (client component)
- [ ] Fetch work item data
- [ ] Fetch decision data
- [ ] Fetch assignee names (from profiles)
- [ ] Implement header section
- [ ] Implement decision card
- [ ] Implement constraints table
- [ ] Implement actions panel
- [ ] Add loading states
- [ ] Add error handling

#### Work Item Detail Components
- [ ] Create `components/work-items/WorkItemHeader.tsx`
- [ ] Create `components/work-items/DecisionCard.tsx`
- [ ] Create `components/work-items/ConstraintsTable.tsx`
- [ ] Create `components/work-items/ActionsPanel.tsx`
- [ ] Create `components/work-items/OverrideModal.tsx`
- [ ] Create `components/work-items/AuditDrawer.tsx`
- [ ] Style all components
- [ ] Implement override workflow
- [ ] Implement mark resolved workflow
- [ ] Implement audit drawer

#### Testing
- [ ] Test work items list with filters
- [ ] Test pagination
- [ ] Test work item detail with decision
- [ ] Test work item detail without decision
- [ ] Test override workflow
- [ ] Test mark resolved workflow
- [ ] Test audit drawer

---

### Phase 4: Decisions

#### Decision Detail Page
- [ ] Create `app/decisions/[work_item_id]/page.tsx` (client component)
- [ ] Fetch audit trail data
- [ ] Implement decision header
- [ ] Implement candidates table
- [ ] Implement constraints list
- [ ] Implement score breakdown chart
- [ ] Add loading states
- [ ] Add error handling

#### Decision Components
- [ ] Create `components/decisions/DecisionHeader.tsx`
- [ ] Create `components/decisions/CandidatesTable.tsx`
- [ ] Create `components/decisions/ConstraintsList.tsx`
- [ ] Create `components/decisions/ScoreBreakdownChart.tsx`
- [ ] Style all components
- [ ] Add expandable score breakdowns

#### Testing
- [ ] Test decision detail with full audit trail
- [ ] Test candidates table with filters
- [ ] Test score breakdown visualization

---

### Phase 5: People

#### People List Page
- [ ] Create `app/people/page.tsx` (client component)
- [ ] Fetch all humans (from all services or new endpoint)
- [ ] Implement table/list
- [ ] Implement filtering
- [ ] Add loading states
- [ ] Add error handling
- [ ] Link rows to detail page

#### Person Detail Page
- [ ] Create `app/people/[human_id]/page.tsx` (client component)
- [ ] Fetch stats data
- [ ] Implement person header
- [ ] Implement service stats grid
- [ ] Implement load metrics
- [ ] Implement activity timeline
- [ ] Add tabs (Overview, Service Stats, Activity)
- [ ] Add loading states
- [ ] Add error handling

#### People Components
- [ ] Create `components/people/PeopleList.tsx`
- [ ] Create `components/people/PersonProfile.tsx`
- [ ] Create `components/people/ServiceStatsGrid.tsx`
- [ ] Create `components/people/LoadMetrics.tsx`
- [ ] Create `components/people/ActivityTimeline.tsx`
- [ ] Style all components

#### Testing
- [ ] Test people list
- [ ] Test person detail with stats
- [ ] Test service stats display
- [ ] Test activity timeline

---

### Phase 6: Create Work Item

#### Create Work Item Page
- [ ] Create `app/work-items/new/page.tsx` (client component)
- [ ] Implement form with validation
- [ ] Implement service select
- [ ] Implement severity select
- [ ] Implement description textarea
- [ ] Implement submit handler
- [ ] Add loading states
- [ ] Add error handling
- [ ] Redirect to detail page on success

#### Create Work Item Components
- [ ] Create `components/work-items/CreateWorkItemForm.tsx`
- [ ] Create `components/work-items/ServiceSelect.tsx`
- [ ] Create `components/work-items/SeveritySelect.tsx`
- [ ] Style all components
- [ ] Add form validation

#### Testing
- [ ] Test form submission
- [ ] Test validation
- [ ] Test redirect after creation
- [ ] Test error handling

---

### Phase 7: Knowledge Graph

#### Graph Page
- [ ] Create `app/graph/page.tsx` (client component)
- [ ] Fetch nodes from database (or create API endpoint)
- [ ] Fetch edges from outcomes table
- [ ] Implement 3D graph component
- [ ] Implement filters
- [ ] Implement node details panel
- [ ] Implement legend
- [ ] Add loading states
- [ ] Add error handling

#### Graph Components
- [ ] Create `components/graph/KnowledgeGraph3D.tsx`
- [ ] Create `components/graph/GraphFilters.tsx`
- [ ] Create `components/graph/NodeDetailsPanel.tsx`
- [ ] Create `components/graph/GraphLegend.tsx`
- [ ] Style all components
- [ ] Implement node interactions (click, hover)
- [ ] Implement graph controls (zoom, rotate, reset)

#### Testing
- [ ] Test graph with real data
- [ ] Test node filtering
- [ ] Test node interactions
- [ ] Test graph controls

---

### Phase 8: Layout & Navigation

#### Layout Components
- [ ] Update `app/layout.tsx` with QueryClientProvider
- [ ] Create `components/layout/Navbar.tsx`
- [ ] Update `components/layout/Sidebar.tsx` with real navigation
- [ ] Update `components/layout/MainLayout.tsx`
- [ ] Style all components
- [ ] Add active route highlighting

#### Navigation
- [ ] Add navigation links to all pages
- [ ] Add breadcrumbs (optional)
- [ ] Add back buttons where needed
- [ ] Test all navigation flows

---

### Phase 9: Polish & Optimization

#### Performance
- [ ] Add React Query caching configuration
- [ ] Implement pagination properly
- [ ] Add loading skeletons
- [ ] Optimize bundle size
- [ ] Add error boundaries

#### UX Improvements
- [ ] Add empty states to all pages
- [ ] Add error states to all pages
- [ ] Add loading states to all pages
- [ ] Add toast notifications for mutations
- [ ] Add confirmation dialogs for destructive actions
- [ ] Add tooltips where helpful

#### Accessibility
- [ ] Add ARIA labels
- [ ] Test keyboard navigation
- [ ] Test screen reader compatibility
- [ ] Add focus management

#### Testing
- [ ] Test all pages with real data
- [ ] Test all user flows end-to-end
- [ ] Test error scenarios
- [ ] Test loading states
- [ ] Test empty states

---

## Testing Strategy

### Unit Tests
- [ ] Test API client functions
- [ ] Test React Query hooks
- [ ] Test utility functions
- [ ] Test component rendering

### Integration Tests
- [ ] Test dashboard data flow
- [ ] Test work items list filtering
- [ ] Test work item detail loading
- [ ] Test override workflow
- [ ] Test create work item flow

### E2E Tests
- [ ] Test complete user journey:
  1. Visit dashboard
  2. View work items list
  3. Click work item → view detail
  4. Override assignment
  5. View decision audit trail
  6. View person stats
  7. Create new work item

### Manual Testing Checklist
- [ ] Test with empty database (no work items)
- [ ] Test with large dataset (1000+ work items)
- [ ] Test with API errors (service down)
- [ ] Test with slow API responses
- [ ] Test on different screen sizes
- [ ] Test in different browsers

---

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_DECISION_URL=http://localhost:8002
NEXT_PUBLIC_LEARNER_URL=http://localhost:8003
NEXT_PUBLIC_GRAPH_URL=http://localhost:8002
```

---

## API Response Types

### Work Item
```typescript
interface WorkItem {
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
}
```

### Decision
```typescript
interface Decision {
  id: string
  work_item_id: string
  primary_human_id: string
  backup_human_ids: string[]
  confidence: number
  constraints_checked: ConstraintResult[]
  created_at: string
}
```

### Audit Trail
```typescript
interface AuditTrail {
  work_item_id: string
  decision_id: string
  decision: Decision
  candidates: Candidate[]
  constraints: ConstraintResult[]
}
```

### Candidate
```typescript
interface Candidate {
  human_id: string
  display_name: string
  fit_score: number
  resolves_count: number
  transfers_count: number
  last_resolved_at?: string
  on_call: boolean
  pages_7d: number
  active_items: number
  filtered: boolean
  filter_reason?: string
  score_breakdown?: ScoreBreakdown
}
```

### Human Stats
```typescript
interface HumanStats {
  human_id: string
  display_name: string
  services: ServiceStats[]
  load: {
    pages_7d: number
    active_items: number
  }
  recent_outcomes: Outcome[]
}
```

---

## Next Steps

1. **Start with Phase 1** - Foundation (API client, React Query setup)
2. **Then Phase 2** - Dashboard (most visible, validates setup)
3. **Then Phase 3** - Work Items (core functionality)
4. **Continue with remaining phases** in order

---

## Notes

- All data comes from APIs - no hardcoded values
- Use React Query for caching and state management
- Add loading/error/empty states to all pages
- Test with real backend services
- Document any API changes needed
- Consider adding API proxy routes if CORS issues occur

---

**Last Updated**: [Current Date]
**Status**: Ready for Implementation

