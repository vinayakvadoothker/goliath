# Person 5: UI (Evidence-First Interface)

## Your Role

You own the **User Interface** - the "window" into the system. This is what people see and interact with.

**Why you?** UI person owns all frontend code and design system. You make the system visible, usable, and beautiful.

---

## What You're Building

### UI Application (`/apps/ui/`)

**The Window** - What people see and interact with:
- Work Items List page (table of all work items)
- Work Item Detail page (decision, evidence, constraints, audit)
- Override workflow (reassign work item)
- Stats display (human capability profiles)
- **Knowledge Graph Visualization** (3D interactive graph)
  - react-force-graph-3d component
  - Load nodes/edges from PostgreSQL
  - 3D coordinates from embedding PCA reduction
  - Color-coded nodes (Humans=blue, WorkItems=red, Services=green, Decisions=purple, Outcomes=amber)
  - Interactive: drag to rotate, scroll to zoom, click for details
  - Filter by node type, time range, service
  - Legend showing node counts

**Why it exists:**
- **Visibility**: People need to see decisions and evidence
- **Reversibility**: Override is the learning signal
- **Trust**: Audit trail must be inspectable
- **Visual understanding**: 3D knowledge graph shows patterns humans can't see in tables

---

## Why You're Doing This

### The UI is the Trust Layer

**People need to:**
- See decisions and evidence (why was this person chosen?)
- Override decisions (this is the learning signal)
- View audit trails (full transparency)
- Understand relationships (3D knowledge graph)

**Without a good UI:**
- System is untrustworthy (can't see why decisions were made)
- Learning loop doesn't work (can't override)
- Demo fails (judges can't see the value)

---

## Complete Work Breakdown

### Hour 1-2: Design System Foundation

**What to create:**
- Initialize Next.js 14 project with shadcn/ui
- Create design system tokens (colors, typography, spacing)
- Build base layout component (off-black bg, off-white text)
- Create typography scale (headings, body, code)
- Setup Tailwind config with design tokens

**Deliverables:**
- ✅ Design system complete
- ✅ Base layout working

### Hour 2-3: Service Scaffolding

**What to create:**
- Create base UI components (Button, Card, Badge, Table)
- Create layout structure (sidebar, main content)
- Add API client utilities (fetch with correlation IDs)
- Setup react-force-graph-3d:
  - Install: `npm install react-force-graph-3d`
  - Create KnowledgeGraph3D component
  - Setup 3D canvas with controls (drag, zoom, rotate)
- Setup graph data fetching:
  - API endpoint: `GET /graph/nodes` (from Decision or new Graph service)
  - Load nodes/edges, apply 3D coordinates
  - Color coding based on node type
- Setup filtering UI:
  - Filter by node type, service, time range
  - Search nodes
  - Temporal slider

**Deliverables:**
- ✅ Base components complete
- ✅ Knowledge graph component scaffolded

### Hour 12-16: UI Foundation

**What to build:**
- Work Items List page
- Work Item Detail page (decision, evidence, constraints, audit)
- Override workflow
- Stats display
- Knowledge Graph Visualization (3D interactive graph)

**Deliverables:**
- ✅ All pages functional
- ✅ Knowledge graph visualization working

### Hour 24-28: UI Polish

**What to polish:**
- Evidence display (collapsible, well-formatted)
- Constraints table (clear pass/fail indicators)
- Audit drawer (readable score breakdown)
- Override flow (smooth, clear feedback)
- Loading states, error states
- Responsive design

**Deliverables:**
- ✅ All UI polished
- ✅ All edge cases handled

### Hour 44-48: UI Completion

**What to complete:**
- All pages functional
- All API integrations working
- Override flow end-to-end
- Stats display
- Error handling
- Loading states

**Deliverables:**
- ✅ All features complete
- ✅ All error states handled

### Hour 64-68: UI Final Polish

**What to polish:**
- Final design pass (spacing, typography, colors)
- Ensure all text is clear and unambiguous
- Add tooltips/explaners where needed
- Test on different screen sizes
- Ensure loading/error states are polished

**Deliverables:**
- ✅ Final polish complete
- ✅ All text is opinionated (no ambiguity)

---

## Design System

### Design Philosophy

**Opinionated, not ambiguous.** Every UI element has:
- Clear purpose (what it does)
- Contextual explanation (why it exists)
- Visual hierarchy (how to read it)

**No questions left unanswered.** If a user wonders "what does this mean?", the design failed.

### Design Tokens

```css
/* Colors */
--bg-primary: #0a0a0a;        /* Off-black background */
--bg-secondary: #141414;     /* Secondary surfaces */
--text-primary: #f5f5f5;     /* Off-white text */
--text-secondary: #a0a0a0;   /* Secondary text */
--border: #1a1a1a;           /* Borders */
--accent-blue: #3b82f6;      /* Blue accent */
--accent-green: #10b981;     /* Green accent */
--accent-red: #ef4444;       /* Red accent */
--accent-purple: #8b5cf6;   /* Purple accent (Decisions) */
--accent-amber: #f59e0b;     /* Amber accent (Outcomes) */

/* Typography */
--font-sans: 'Inter', -apple-system, sans-serif;
--font-mono: 'Fira Code', monospace;

/* Spacing */
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;

/* Border radius */
--radius-sm: 0.25rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
```

### Typography Scale

```css
/* Headings */
h1 { font-size: 2rem; font-weight: 700; line-height: 1.2; }
h2 { font-size: 1.5rem; font-weight: 600; line-height: 1.3; }
h3 { font-size: 1.25rem; font-weight: 600; line-height: 1.4; }

/* Body */
body { font-size: 1rem; font-weight: 400; line-height: 1.6; }
small { font-size: 0.875rem; }

/* Code */
code { font-family: var(--font-mono); font-size: 0.875rem; }
```

---

## Application Structure

### Layout Architecture

```
/apps/ui/
├── app/
│   ├── layout.tsx              # Root layout (navbar, sidebar)
│   ├── page.tsx                 # Dashboard/Home
│   ├── work-items/
│   │   ├── page.tsx            # Work Items List
│   │   └── [id]/
│   │       └── page.tsx        # Work Item Detail
│   ├── graph/
│   │   └── page.tsx            # Knowledge Graph 3D
│   ├── stats/
│   │   └── [human_id]/
│   │       └── page.tsx        # Human Stats
│   └── api/                     # API routes (if needed)
├── components/
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── MainLayout.tsx
│   ├── work-items/
│   │   ├── WorkItemsList.tsx
│   │   ├── WorkItemDetail.tsx
│   │   ├── OverrideModal.tsx
│   │   └── AuditDrawer.tsx
│   ├── graph/
│   │   └── KnowledgeGraph3D.tsx
│   ├── stats/
│   │   └── HumanStats.tsx
│   └── ui/                      # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── table.tsx
│       ├── badge.tsx
│       ├── dialog.tsx
│       ├── drawer.tsx
│       └── ...
└── lib/
    ├── api-client.ts
    └── utils.ts
```

### Root Layout (`app/layout.tsx`)

**Structure:**
- Navbar (top)
- Sidebar (left)
- Main content area (right)
- All pages use this layout

**Design:**
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-[#0a0a0a] text-[#f5f5f5]">
          <Navbar />
          <div className="flex">
            <Sidebar />
            <main className="flex-1 p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
```

### Navbar Component

**Location**: `components/layout/Navbar.tsx`

**What it shows:**
- Logo/Brand name: "Goliath"
- Navigation links (Work Items, Graph, Stats)
- User menu (if needed)
- Status indicator (system health)

**Design:**
```tsx
<nav className="border-b border-[#1a1a1a] bg-[#141414] px-6 py-4">
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-6">
      <h1 className="text-xl font-bold">Goliath</h1>
      <NavLinks />
    </div>
    <div className="flex items-center gap-4">
      <StatusIndicator />
      <UserMenu />
    </div>
  </div>
</nav>
```

**NavLinks:**
- Work Items (link to `/work-items`)
- Knowledge Graph (link to `/graph`)
- Stats (dropdown: "View All Stats" or search)

### Sidebar Component

**Location**: `components/layout/Sidebar.tsx`

**What it shows:**
- Quick filters (Service, Severity)
- Recent work items (last 5)
- Quick actions (Create Work Item button)
- System status (if needed)

**Design:**
```tsx
<aside className="w-64 border-r border-[#1a1a1a] bg-[#141414] p-4">
  <div className="space-y-6">
    {/* Quick Filters */}
    <div>
      <h3 className="text-sm font-semibold mb-2">Quick Filters</h3>
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Service" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Services</SelectItem>
          <SelectItem value="api-service">API Service</SelectItem>
          <SelectItem value="payment-service">Payment Service</SelectItem>
        </SelectContent>
      </Select>
      {/* Severity filter */}
    </div>

    {/* Recent Work Items */}
    <div>
      <h3 className="text-sm font-semibold mb-2">Recent</h3>
      <ul className="space-y-2">
        {recentWorkItems.map(item => (
          <li key={item.id}>
            <Link href={`/work-items/${item.id}`} className="text-sm hover:text-[#3b82f6]">
              {item.service} - {item.severity}
            </Link>
          </li>
        ))}
      </ul>
    </div>

    {/* Quick Actions */}
    <Button onClick={() => navigate('/work-items/new')}>
      Create Work Item
    </Button>
  </div>
</aside>
```

### Main Layout Component

**Location**: `components/layout/MainLayout.tsx`

**Wrapper for all pages:**
```tsx
export function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="container mx-auto max-w-7xl">
      {children}
    </div>
  );
}
```

---

## Pages & Components

### Home/Dashboard Page (`app/page.tsx`)

**Route**: `/`

**What it shows:**
- Overview stats (total work items, active, resolved)
- Recent decisions (last 5)
- System status
- Quick actions

**Design:**
```tsx
<div className="dashboard">
  <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
  
  {/* Stats Grid */}
  <div className="grid grid-cols-4 gap-4 mb-6">
    <StatCard label="Total Work Items" value={totalWorkItems} />
    <StatCard label="Active" value={activeWorkItems} />
    <StatCard label="Resolved" value={resolvedWorkItems} />
    <StatCard label="Avg Resolution Time" value={avgResolutionTime} />
  </div>

  {/* Recent Decisions */}
  <Card>
    <CardHeader>
      <h2>Recent Decisions</h2>
    </CardHeader>
    <CardContent>
      <RecentDecisionsList limit={5} />
    </CardContent>
  </Card>
</div>
```

### 1. Work Items List Page

**Route**: `/work-items`

**Page Structure:**
- Header: "Work Items" title + "Create New" button
- Filters bar: Service dropdown, Severity dropdown, Search input
- Table: All work items with pagination
- Footer: Pagination controls

**What it shows:**
- Table of all work items
- Columns: ID, Service, Severity, Created, Status, Actions
- Filter by service, severity
- Search by ID or description
- Click row → navigate to detail
- Pagination (50 items per page, max 100)

**Design:**
```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>ID</TableHead>
      <TableHead>Service</TableHead>
      <TableHead>Severity</TableHead>
      <TableHead>Created</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Actions</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {workItems.map(item => (
      <TableRow key={item.id} onClick={() => navigate(`/work-items/${item.id}`)}>
        <TableCell>{item.id}</TableCell>
        <TableCell>{item.service}</TableCell>
        <TableCell>
          <Badge variant={getSeverityVariant(item.severity)}>
            {item.severity}
          </Badge>
        </TableCell>
        <TableCell>{formatDate(item.created_at)}</TableCell>
        <TableCell>{item.status}</TableCell>
        <TableCell>
          <Button variant="ghost" size="sm">View</Button>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

**Filters:**
- Service dropdown (multi-select)
- Severity dropdown (multi-select)
- Search bar (by ID, description)

### 2. Work Item Detail Page

**Route**: `/work-items/[id]/page.tsx`

**Page Structure:**
- Breadcrumb: Home > Work Items > [Work Item ID]
- Header section: Service, Severity, Created, Status badges
- Main content (2-column layout):
  - Left column: Decision Card
  - Right column: Actions + Stats
- Bottom section: Audit drawer trigger

**What it shows:**
- **Header Section:**
  - Service name (large)
  - Severity badge (color-coded)
  - Created timestamp
  - Status badge (open/assigned/resolved)
  - Back button (to work items list)

- **Decision Card (Left Column):**
  - Primary assignee (large, prominent with avatar)
  - Backup assignees (smaller, horizontal list)
  - Confidence badge (progress bar with color)
  - Evidence bullets (collapsible section)
  - Constraints table (pass/fail with icons)
  - "Why not next best" section (collapsible)

- **Actions Card (Right Column):**
  - Override button (opens modal)
  - Mark resolved button
  - View in Jira button (if jira_issue_key exists)
  - View Stats button (links to human stats page)

- **Audit Drawer (Slide-out from right):**
  - Trigger: "View Audit Trail" button
  - Candidate set with scores (table)
  - Filter reasons (why candidates were filtered)
  - Score breakdown (bar chart or table)
  - Full decision reasoning chain

**Design:**
```tsx
<div className="work-item-detail">
  {/* Header */}
  <div className="header">
    <h1>{workItem.service}</h1>
    <Badge variant={getSeverityVariant(workItem.severity)}>
      {workItem.severity}
    </Badge>
    <span className="created">{formatDate(workItem.created_at)}</span>
  </div>

  {/* Decision Card */}
  <Card>
    <CardHeader>
      <h2>Decision</h2>
      <ConfidenceBadge confidence={decision.confidence} />
    </CardHeader>
    <CardContent>
      {/* Primary Assignee */}
      <div className="primary-assignee">
        <Avatar>
          <AvatarFallback>{getInitials(primaryHuman.display_name)}</AvatarFallback>
        </Avatar>
        <div>
          <h3>{primaryHuman.display_name}</h3>
          <p>Primary Assignee</p>
        </div>
      </div>

      {/* Backup Assignees */}
      <div className="backup-assignees">
        <h4>Backup Assignees</h4>
        {backupHumans.map(human => (
          <Badge key={human.id} variant="outline">{human.display_name}</Badge>
        ))}
      </div>

      {/* Evidence */}
      <Collapsible>
        <CollapsibleTrigger>Evidence ({evidence.length})</CollapsibleTrigger>
        <CollapsibleContent>
          <ul>
            {evidence.map((e, i) => (
              <li key={i}>
                <EvidenceBullet type={e.type} text={e.text} timeWindow={e.time_window} />
              </li>
            ))}
          </ul>
        </CollapsibleContent>
      </Collapsible>

      {/* Constraints */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Constraint</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Reason</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {constraints.map(c => (
            <TableRow key={c.name}>
              <TableCell>{c.name}</TableCell>
              <TableCell>
                {c.passed ? (
                  <CheckCircle className="text-green-500" />
                ) : (
                  <XCircle className="text-red-500" />
                )}
              </TableCell>
              <TableCell>{c.reason}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>

  {/* Actions */}
  <div className="actions">
    <Button onClick={() => setOverrideModalOpen(true)}>Override</Button>
    <Button variant="outline" onClick={() => markResolved()}>Mark Resolved</Button>
  </div>

  {/* Audit Drawer */}
  <Drawer>
    <DrawerTrigger>View Audit Trail</DrawerTrigger>
    <DrawerContent>
      <AuditTrail workItemId={workItem.id} />
    </DrawerContent>
  </Drawer>
</div>
```

### 3. Override Modal Component

**Location**: `components/work-items/OverrideModal.tsx`

**Trigger**: "Override" button on Work Item Detail page

**What it shows:**
- Modal overlay (dark background)
- Modal content (centered card):
  - Title: "Override Assignment"
  - Description: "Reassign this work item to a different person. This will update the learning system."
  - Form:
    - Current assignee display (read-only)
    - New assignee dropdown (searchable, shows fit_score)
    - Reason textarea (optional, placeholder: "Why are you overriding?")
    - Warning message: "This will decrease the original assignee's fit_score and update the learning system."
  - Actions:
    - Cancel button (closes modal)
    - Submit button (primary, "Reassign")

**Design:**
```tsx
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent className="bg-[#141414] border-[#1a1a1a]">
    <DialogHeader>
      <DialogTitle>Override Assignment</DialogTitle>
      <DialogDescription className="text-[#a0a0a0]">
        Reassign this work item to a different person. This will update the learning system.
      </DialogDescription>
    </DialogHeader>
    <form onSubmit={handleSubmit}>
      {/* Current Assignee */}
      <div className="mb-4">
        <Label>Current Assignee</Label>
        <div className="p-3 bg-[#0a0a0a] rounded border border-[#1a1a1a]">
          {currentAssignee.display_name}
        </div>
      </div>

      {/* New Assignee */}
      <div className="mb-4">
        <Label>New Assignee</Label>
        <Select value={newAssigneeId} onValueChange={setNewAssigneeId}>
          <SelectTrigger>
            <SelectValue placeholder="Select new assignee" />
          </SelectTrigger>
          <SelectContent>
            {availableHumans.map(human => (
              <SelectItem key={human.id} value={human.id}>
                <div className="flex items-center justify-between">
                  <span>{human.display_name}</span>
                  <Badge variant="outline">Fit: {(human.fit_score * 100).toFixed(0)}%</Badge>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Reason */}
      <div className="mb-4">
        <Label>Reason (Optional)</Label>
        <Textarea
          placeholder="Why are you overriding this assignment?"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={3}
        />
      </div>

      {/* Warning */}
      <Alert variant="warning" className="mb-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          This will decrease {currentAssignee.display_name}'s fit_score and update the learning system.
        </AlertDescription>
      </Alert>

      {/* Actions */}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button type="submit" variant="default">
          Reassign
        </Button>
      </div>
    </form>
  </DialogContent>
</Dialog>
```

**Design:**
```tsx
<Dialog open={overrideModalOpen} onOpenChange={setOverrideModalOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Override Assignment</DialogTitle>
      <DialogDescription>
        Reassign this work item to a different person. This will update the learning system.
      </DialogDescription>
    </DialogHeader>
    <form onSubmit={handleOverride}>
      <Select value={newAssigneeId} onValueChange={setNewAssigneeId}>
        <SelectTrigger>
          <SelectValue placeholder="Select new assignee" />
        </SelectTrigger>
        <SelectContent>
          {availableHumans.map(human => (
            <SelectItem key={human.id} value={human.id}>
              {human.display_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Textarea
        placeholder="Reason (optional)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
      />
      <Button type="submit">Reassign</Button>
    </form>
  </DialogContent>
</Dialog>
```

**Processing:**
- Calls `POST /work-items/:id/outcome` with type="reassigned"
- Updates UI to show new assignee
- Refreshes stats display

### 4. Knowledge Graph Visualization Page

**Route**: `/graph/page.tsx`

**Page Structure:**
- Header: "Knowledge Graph" title + filter controls
- Main area: 3D graph canvas (full width/height)
- Sidebar (right): Node details panel (when node selected)
- Footer: Legend + controls

**What it shows:**
- **Header Section:**
  - Title: "Knowledge Graph"
  - Filter controls:
    - Node type dropdown (All, Humans, Work Items, Services, Decisions, Outcomes)
    - Service dropdown (All, api-service, payment-service, etc.)
    - Time range slider (last 7 days, 30 days, 90 days, all time)
    - Search input (search nodes by name/ID)
    - Reset view button (auto-zoom to fit all nodes)

- **3D Graph Canvas (Main Area):**
  - Full-width, full-height canvas
  - Nodes: Humans (blue #3b82f6), WorkItems (red #ef4444), Services (green #10b981), Decisions (purple #8b5cf6), Outcomes (amber #f59e0b)
  - Edges: RESOLVED (green), TRANSFERRED (red), CO_WORKED (blue) - all timestamped
  - Interactive controls:
    - Drag to rotate
    - Scroll to zoom
    - Click node → show details in sidebar
    - Hover node → highlight connected nodes
    - Right-click → context menu (view details, filter by node, etc.)

- **Sidebar (Right, when node selected):**
  - Node type badge
  - Node name/ID
  - Node details (depends on type):
    - Human: Stats, recent work items, connections
    - Work Item: Description, severity, assignee, status
    - Service: Work items count, active incidents
    - Decision: Confidence, assignee, evidence count
    - Outcome: Type, timestamp, actors
  - "View Full Details" button (navigates to detail page)

- **Legend (Bottom):**
  - Node type counts (Humans: 200, Work Items: 150, etc.)
  - Color coding reference
  - Edge type legend

- **Controls (Bottom Right):**
  - Auto-zoom button
  - Reset camera button
  - Toggle edges button
  - Node size slider
  - Edge width slider

**Design:**
```tsx
import ForceGraph3D from 'react-force-graph-3d';

function KnowledgeGraph3D() {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [filters, setFilters] = useState({
    nodeType: 'all',
    service: 'all',
    timeRange: 'all'
  });

  useEffect(() => {
    // Fetch nodes/edges from API
    fetch('/api/graph/nodes', {
      params: filters
    }).then(res => res.json())
      .then(data => {
        setNodes(data.nodes);
        setLinks(data.links);
      });
  }, [filters]);

  return (
    <div className="knowledge-graph">
      {/* Filters */}
      <div className="filters">
        <Select value={filters.nodeType} onValueChange={(v) => setFilters({...filters, nodeType: v})}>
          <SelectTrigger>
            <SelectValue placeholder="Node Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="human">Humans</SelectItem>
            <SelectItem value="work_item">Work Items</SelectItem>
            <SelectItem value="service">Services</SelectItem>
          </SelectContent>
        </Select>
        {/* ... other filters */}
      </div>

      {/* 3D Graph */}
      <ForceGraph3D
        graphData={{ nodes, links }}
        nodeLabel={node => `${node.type}: ${node.name}`}
        nodeColor={node => {
          switch (node.type) {
            case 'human': return '#3b82f6'; // Blue
            case 'work_item': return '#ef4444'; // Red
            case 'service': return '#10b981'; // Green
            case 'decision': return '#8b5cf6'; // Purple
            case 'outcome': return '#f59e0b'; // Amber
            default: return '#666';
          }
        }}
        nodeVal={node => node.size || 5}
        linkColor={link => '#555'}
        linkWidth={link => link.width || 1}
        onNodeClick={node => {
          // Show node details in sidebar
          setSelectedNode(node);
        }}
        onNodeHover={node => {
          // Highlight connected nodes
          highlightConnectedNodes(node);
        }}
        enableNodeDrag={true}
        cooldownTicks={100}
        onEngineStop={() => {
          // Graph stabilized
        }}
      />

      {/* Legend */}
      <div className="legend">
        <LegendItem color="#3b82f6" label="Humans" count={nodeCounts.humans} />
        <LegendItem color="#ef4444" label="Work Items" count={nodeCounts.work_items} />
        <LegendItem color="#10b981" label="Services" count={nodeCounts.services} />
        <LegendItem color="#8b5cf6" label="Decisions" count={nodeCounts.decisions} />
        <LegendItem color="#f59e0b" label="Outcomes" count={nodeCounts.outcomes} />
      </div>
    </div>
  );
}
```

**API Integration:**
- Calls `GET /graph/nodes` (from Decision service or new Graph service)
- Loads nodes with 3D coordinates (embedding_3d_x, embedding_3d_y, embedding_3d_z)
- Loads edges (RESOLVED, TRANSFERRED, CO_WORKED)
- Applies filters (node type, service, time range)

### 5. Human Stats Page

**Route**: `/stats/[human_id]/page.tsx`

**Page Structure:**
- Header: Human name + avatar
- Tabs: Overview, Service Stats, Activity Timeline
- Main content: Stats cards and charts

**What it shows:**
- **Header Section:**
  - Human avatar (initials or image)
  - Human display name (large)
  - Contact info (Slack handle, email)
  - Back button

- **Overview Tab:**
  - Summary stats card:
    - Total resolves (all services)
    - Total transfers (all services)
    - Overall fit_score (weighted average)
    - Current load (pages_7d, active_items)
  - Service breakdown (pie chart or list)
  - Recent activity (last 10 outcomes)

- **Service Stats Tab:**
  - Per-service cards:
    - Service name
    - Fit score (progress bar + percentage)
    - Resolves count (last 90 days)
    - Transfers count (last 90 days)
    - Last resolved date
    - Resolved by severity breakdown (sev1: 3, sev2: 5, etc.)
  - Chart: Fit score over time (line chart)

- **Activity Timeline Tab:**
  - Chronological list of outcomes:
    - Resolved work items (with links)
    - Transferred work items (with links)
    - Timestamps
    - Service context

- **Actions:**
  - "View in Knowledge Graph" button (filters graph to this human)
  - "View Recent Work Items" button (filters work items list)

**Design:**
```tsx
<div className="stats-page">
  <h1>{human.display_name}</h1>
  
  {/* Service Stats */}
  <Card>
    <CardHeader>
      <h2>Service Capabilities</h2>
    </CardHeader>
    <CardContent>
      {serviceStats.map(stat => (
        <div key={stat.service} className="service-stat">
          <h3>{stat.service}</h3>
          <div className="metrics">
            <Metric label="Fit Score" value={stat.fit_score} format="percentage" />
            <Metric label="Resolves" value={stat.resolves_count} />
            <Metric label="Transfers" value={stat.transfers_count} />
            <Metric label="Last Resolved" value={formatDate(stat.last_resolved_at)} />
          </div>
        </div>
      ))}
    </CardContent>
  </Card>

  {/* Load Stats */}
  <Card>
    <CardHeader>
      <h2>Current Load</h2>
    </CardHeader>
    <CardContent>
      <Metric label="Pages (7d)" value={load.pages_7d} />
      <Metric label="Active Items" value={load.active_items} />
    </CardContent>
  </Card>
</div>
```

---

## Component Library

### Base Components (shadcn/ui)

**Required components:**
- `Button` - Primary, secondary, outline, ghost variants
- `Card` - Container for content sections
- `Badge` - Status indicators, labels
- `Table` - Data tables
- `Dialog` - Modals
- `Drawer` - Slide-out panels
- `Select` - Dropdowns
- `Input` - Text inputs
- `Textarea` - Multi-line inputs
- `Avatar` - User avatars
- `Collapsible` - Expandable sections
- `Alert` - Warning/info messages
- `Progress` - Progress bars
- `Tabs` - Tab navigation
- `Tooltip` - Hover tooltips

**Custom components:**
- `EvidenceBullet` - Evidence display with icon + text
- `ConfidenceBadge` - Confidence score display
- `SeverityBadge` - Severity indicator
- `Metric` - Stat display (label + value)
- `StatCard` - Dashboard stat cards
- `NodeDetails` - Knowledge graph node details panel
- `AuditTrail` - Full audit trace display
- `ScoreBreakdown` - Score visualization (bar chart)

### Component Specifications

#### EvidenceBullet Component

**Location**: `components/work-items/EvidenceBullet.tsx`

**Props:**
```typescript
interface EvidenceBulletProps {
  type: 'recent_resolution' | 'on_call' | 'low_load' | 'similar_incident' | 'fit_score';
  text: string;
  timeWindow: string;
  source: string;
}
```

**Design:**
- Icon based on type (CheckCircle, Clock, TrendingDown, etc.)
- Text with time window highlighted
- Source badge (small, muted)

#### ConfidenceBadge Component

**Location**: `components/work-items/ConfidenceBadge.tsx`

**Props:**
```typescript
interface ConfidenceBadgeProps {
  confidence: number; // 0-1
}
```

**Design:**
- Progress bar with color:
  - Green (>0.7): High confidence
  - Yellow (0.4-0.7): Medium confidence
  - Red (<0.4): Low confidence
- Percentage display
- Tooltip: "Confidence based on top1-top2 score margin"

#### SeverityBadge Component

**Location**: `components/shared/SeverityBadge.tsx`

**Props:**
```typescript
interface SeverityBadgeProps {
  severity: 'sev1' | 'sev2' | 'sev3' | 'sev4';
}
```

**Design:**
- Color-coded:
  - sev1: Red (#ef4444)
  - sev2: Orange (#f59e0b)
  - sev3: Yellow (#eab308)
  - sev4: Gray (#6b7280)
- Uppercase text: "SEV1", "SEV2", etc.

---

## Routing Structure

### Next.js App Router Routes

```
/apps/ui/app/
├── layout.tsx                    # Root layout (Navbar + Sidebar)
├── page.tsx                      # Dashboard (/)
├── work-items/
│   ├── page.tsx                  # List (/work-items)
│   ├── new/
│   │   └── page.tsx              # Create new (/work-items/new)
│   └── [id]/
│       └── page.tsx              # Detail (/work-items/:id)
├── graph/
│   └── page.tsx                  # Knowledge Graph (/graph)
└── stats/
    ├── page.tsx                  # Stats list/search (/stats)
    └── [human_id]/
        └── page.tsx              # Human stats (/stats/:human_id)
```

### Navigation Structure

**Navbar Links:**
- Home (/) - Dashboard
- Work Items (/work-items) - List of all work items
- Knowledge Graph (/graph) - 3D visualization
- Stats (/stats) - Stats search/list

**Sidebar Quick Links:**
- Recent Work Items (last 5, clickable)
- Quick Filters (Service, Severity)
- Create Work Item button

**Breadcrumbs:**
- Home > Work Items > [Work Item ID]
- Home > Stats > [Human Name]
- Home > Knowledge Graph

---

## API Integration

### API Client

```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function fetchWithCorrelationId(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const correlationId = generateCorrelationId();
  
  return fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
      'x-correlation-id': correlationId,
    },
  });
}

// Work Items
export async function getWorkItems(filters?: WorkItemFilters): Promise<WorkItem[]> {
  const params = new URLSearchParams(filters as any);
  const response = await fetchWithCorrelationId(`/work-items?${params}`);
  return response.json();
}

export async function getWorkItem(id: string): Promise<WorkItem> {
  const response = await fetchWithCorrelationId(`/work-items/${id}`);
  return response.json();
}

export async function createWorkItem(data: CreateWorkItemData): Promise<WorkItem> {
  const response = await fetchWithCorrelationId('/work-items', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
}

export async function recordOutcome(
  workItemId: string,
  outcome: OutcomeData
): Promise<Outcome> {
  const response = await fetchWithCorrelationId(`/work-items/${workItemId}/outcome`, {
    method: 'POST',
    body: JSON.stringify(outcome),
  });
  return response.json();
}

// Decisions
export async function getDecision(workItemId: string): Promise<Decision> {
  const response = await fetchWithCorrelationId(`/decisions/${workItemId}`);
  return response.json();
}

export async function getAudit(workItemId: string): Promise<AuditTrail> {
  const response = await fetchWithCorrelationId(`/audit/${workItemId}`);
  return response.json();
}

// Learner
export async function getStats(humanId: string): Promise<HumanStats> {
  const response = await fetchWithCorrelationId(`/stats?human_id=${humanId}`);
  return response.json();
}

// Graph
export async function getGraphNodes(filters?: GraphFilters): Promise<GraphData> {
  const params = new URLSearchParams(filters as any);
  const response = await fetchWithCorrelationId(`/graph/nodes?${params}`);
  return response.json();
}
```

---

## How to Test

### Standalone Testing (Without Other Services)

**1. Create test script: `/apps/ui/scripts/test_standalone.sh`**

```bash
#!/bin/bash
# Test UI standalone

# Install dependencies
npm install

# Run tests
npm run test

# Run dev server (with mocked APIs)
npm run dev
```

**2. Create mock API responses:**

```typescript
// lib/mock-api.ts
export const mockWorkItems = [
  {
    id: "wi_1",
    service: "api-service",
    severity: "sev1",
    description: "High error rate detected",
    created_at: "2024-01-15T10:30:00Z",
    status: "assigned"
  }
];

export const mockDecision = {
  decision_id: "dec_1",
  work_item_id: "wi_1",
  primary_human_id: "human_1",
  backup_human_ids: ["human_2"],
  confidence: 0.85,
  evidence: [
    {
      type: "recent_resolution",
      text: "Resolved 3 similar incidents in last 7 days",
      time_window: "last 7 days",
      source: "Learner stats"
    }
  ],
  constraints_checked: [
    { name: "on_call_required", passed: true, reason: "Currently on-call" }
  ]
};
```

**3. Test cases:**

```typescript
// __tests__/work-items-list.test.tsx
describe('WorkItemsList', () => {
  it('renders work items table', () => {
    render(<WorkItemsList />);
    expect(screen.getByText('api-service')).toBeInTheDocument();
  });

  it('filters by service', () => {
    render(<WorkItemsList />);
    fireEvent.change(screen.getByLabelText('Service'), { target: { value: 'api-service' } });
    expect(screen.getAllByText('api-service')).toHaveLength(1);
  });
});

// __tests__/work-item-detail.test.tsx
describe('WorkItemDetail', () => {
  it('displays decision with evidence', () => {
    render(<WorkItemDetail workItemId="wi_1" />);
    expect(screen.getByText('Resolved 3 similar incidents')).toBeInTheDocument();
  });

  it('opens override modal', () => {
    render(<WorkItemDetail workItemId="wi_1" />);
    fireEvent.click(screen.getByText('Override'));
    expect(screen.getByText('Override Assignment')).toBeInTheDocument();
  });
});

// __tests__/knowledge-graph.test.tsx
describe('KnowledgeGraph3D', () => {
  it('renders 3D graph', () => {
    render(<KnowledgeGraph3D />);
    expect(screen.getByTestId('force-graph-3d')).toBeInTheDocument();
  });

  it('filters nodes by type', () => {
    render(<KnowledgeGraph3D />);
    fireEvent.change(screen.getByLabelText('Node Type'), { target: { value: 'human' } });
    // Check only human nodes are visible
  });
});
```

---

## Complete Page Specifications

### Dashboard Page (`app/page.tsx`)

**Full Structure:**
```tsx
<MainLayout>
  <div className="dashboard-page">
    {/* Header */}
    <div className="flex items-center justify-between mb-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <Button onClick={() => navigate('/work-items/new')}>
        Create Work Item
      </Button>
    </div>

    {/* Stats Grid */}
    <div className="grid grid-cols-4 gap-4 mb-6">
      <StatCard
        label="Total Work Items"
        value={stats.total}
        trend="up"
        trendValue="+12%"
      />
      <StatCard
        label="Active"
        value={stats.active}
        color="blue"
      />
      <StatCard
        label="Resolved (7d)"
        value={stats.resolved_7d}
        color="green"
      />
      <StatCard
        label="Avg Resolution"
        value={stats.avg_resolution_time}
        unit="hours"
      />
    </div>

    {/* Recent Decisions */}
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Recent Decisions</h2>
          <Link href="/work-items" className="text-sm text-[#3b82f6]">
            View All
          </Link>
        </div>
      </CardHeader>
      <CardContent>
        <RecentDecisionsList limit={5} />
      </CardContent>
    </Card>

    {/* System Status */}
    <Card>
      <CardHeader>
        <h2 className="text-xl font-semibold">System Status</h2>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <StatusIndicator service="Decision" status="healthy" />
          <StatusIndicator service="Learner" status="healthy" />
          <StatusIndicator service="Executor" status="healthy" />
        </div>
      </CardContent>
    </Card>
  </div>
</MainLayout>
```

### Work Items List Page (`app/work-items/page.tsx`)

**Full Structure:**
```tsx
<MainLayout>
  <div className="work-items-list-page">
    {/* Header */}
    <div className="flex items-center justify-between mb-6">
      <h1 className="text-3xl font-bold">Work Items</h1>
      <Button onClick={() => navigate('/work-items/new')}>
        Create New
      </Button>
    </div>

    {/* Filters Bar */}
    <div className="flex gap-4 mb-6 p-4 bg-[#141414] rounded-lg border border-[#1a1a1a]">
      <Select value={filters.service} onValueChange={(v) => setFilters({...filters, service: v})}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="All Services" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Services</SelectItem>
          <SelectItem value="api-service">API Service</SelectItem>
          <SelectItem value="payment-service">Payment Service</SelectItem>
        </SelectContent>
      </Select>

      <Select value={filters.severity} onValueChange={(v) => setFilters({...filters, severity: v})}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="All Severities" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Severities</SelectItem>
          <SelectItem value="sev1">SEV1</SelectItem>
          <SelectItem value="sev2">SEV2</SelectItem>
          <SelectItem value="sev3">SEV3</SelectItem>
          <SelectItem value="sev4">SEV4</SelectItem>
        </SelectContent>
      </Select>

      <Input
        placeholder="Search by ID or description..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="flex-1"
      />
    </div>

    {/* Table */}
    <Card>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Service</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Assignee</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {workItems.map(item => (
            <TableRow
              key={item.id}
              className="cursor-pointer hover:bg-[#141414]"
              onClick={() => navigate(`/work-items/${item.id}`)}
            >
              <TableCell className="font-mono text-sm">{item.id}</TableCell>
              <TableCell>{item.service}</TableCell>
              <TableCell>
                <SeverityBadge severity={item.severity} />
              </TableCell>
              <TableCell>{formatDate(item.created_at)}</TableCell>
              <TableCell>
                <Badge variant={getStatusVariant(item.status)}>
                  {item.status}
                </Badge>
              </TableCell>
              <TableCell>{item.assignee?.display_name || 'Unassigned'}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <Button variant="ghost" size="sm">
                  View
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>

    {/* Pagination */}
    <div className="flex items-center justify-between mt-6">
      <div className="text-sm text-[#a0a0a0]">
        Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
      </div>
      <div className="flex gap-2">
        <Button
          variant="outline"
          disabled={offset === 0}
          onClick={() => setOffset(offset - limit)}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          disabled={offset + limit >= total}
          onClick={() => setOffset(offset + limit)}
        >
          Next
        </Button>
      </div>
    </div>
  </div>
</MainLayout>
```

### Work Item Detail Page (`app/work-items/[id]/page.tsx`)

**Full Structure:**
```tsx
<MainLayout>
  <div className="work-item-detail-page">
    {/* Breadcrumb */}
    <nav className="mb-4 text-sm text-[#a0a0a0]">
      <Link href="/" className="hover:text-[#f5f5f5]">Home</Link>
      {' > '}
      <Link href="/work-items" className="hover:text-[#f5f5f5]">Work Items</Link>
      {' > '}
      <span className="text-[#f5f5f5]">{workItem.id}</span>
    </nav>

    {/* Header */}
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center gap-4">
        <h1 className="text-3xl font-bold">{workItem.service}</h1>
        <SeverityBadge severity={workItem.severity} />
        <Badge variant="outline">{workItem.status}</Badge>
        <span className="text-sm text-[#a0a0a0]">
          Created {formatDate(workItem.created_at)}
        </span>
      </div>
      <Button variant="outline" onClick={() => navigate('/work-items')}>
        Back to List
      </Button>
    </div>

    {/* Main Content (2-column layout) */}
    <div className="grid grid-cols-3 gap-6">
      {/* Left Column (Decision Card) */}
      <div className="col-span-2">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Decision</h2>
              <ConfidenceBadge confidence={decision.confidence} />
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Primary Assignee */}
            <div className="flex items-center gap-4 p-4 bg-[#0a0a0a] rounded-lg border border-[#1a1a1a]">
              <Avatar className="h-16 w-16">
                <AvatarFallback className="text-lg">
                  {getInitials(primaryHuman.display_name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="text-xl font-semibold">{primaryHuman.display_name}</h3>
                <p className="text-sm text-[#a0a0a0]">Primary Assignee</p>
                <div className="flex gap-2 mt-2">
                  <Badge variant="outline">Fit: {(primaryHuman.fit_score * 100).toFixed(0)}%</Badge>
                  {primaryHuman.on_call && <Badge variant="default">On-Call</Badge>}
                </div>
              </div>
            </div>

            {/* Backup Assignees */}
            <div>
              <h4 className="text-sm font-semibold mb-2">Backup Assignees</h4>
              <div className="flex gap-2">
                {backupHumans.map(human => (
                  <Badge key={human.id} variant="outline">
                    {human.display_name}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Evidence */}
            <Collapsible>
              <CollapsibleTrigger className="flex items-center gap-2">
                <ChevronDown className="h-4 w-4" />
                <span className="font-semibold">Evidence ({evidence.length})</span>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-4 space-y-2">
                {evidence.map((e, i) => (
                  <EvidenceBullet
                    key={i}
                    type={e.type}
                    text={e.text}
                    timeWindow={e.time_window}
                    source={e.source}
                  />
                ))}
              </CollapsibleContent>
            </Collapsible>

            {/* Why Not Next Best */}
            {whyNotNextBest.length > 0 && (
              <Collapsible>
                <CollapsibleTrigger className="flex items-center gap-2">
                  <ChevronDown className="h-4 w-4" />
                  <span className="font-semibold">Why Not Next Best</span>
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-4">
                  <ul className="list-disc list-inside space-y-1">
                    {whyNotNextBest.map((reason, i) => (
                      <li key={i} className="text-sm">{reason}</li>
                    ))}
                  </ul>
                </CollapsibleContent>
              </Collapsible>
            )}

            {/* Constraints */}
            <div>
              <h4 className="text-sm font-semibold mb-2">Constraints Checked</h4>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Constraint</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Reason</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {constraints.map(c => (
                    <TableRow key={c.name}>
                      <TableCell className="font-mono text-sm">{c.name}</TableCell>
                      <TableCell>
                        {c.passed ? (
                          <CheckCircle className="h-5 w-5 text-[#10b981]" />
                        ) : (
                          <XCircle className="h-5 w-5 text-[#ef4444]" />
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-[#a0a0a0]">{c.reason}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right Column (Actions) */}
      <div className="col-span-1">
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Actions</h3>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              className="w-full"
              onClick={() => setOverrideModalOpen(true)}
            >
              Override Assignment
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => markResolved()}
            >
              Mark Resolved
            </Button>
            {workItem.jira_issue_key && (
              <Button
                variant="outline"
                className="w-full"
                onClick={() => window.open(`https://jira.example.com/browse/${workItem.jira_issue_key}`)}
              >
                View in Jira
              </Button>
            )}
            <Button
              variant="ghost"
              className="w-full"
              onClick={() => navigate(`/stats/${primaryHuman.id}`)}
            >
              View Assignee Stats
            </Button>
          </CardContent>
        </Card>

        {/* Stats Card */}
        <Card className="mt-4">
          <CardHeader>
            <h3 className="font-semibold">Quick Stats</h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Metric label="Confidence" value={`${(decision.confidence * 100).toFixed(0)}%`} />
              <Metric label="Evidence Points" value={evidence.length} />
              <Metric label="Constraints Passed" value={constraints.filter(c => c.passed).length} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    {/* Audit Drawer Trigger */}
    <div className="mt-6">
      <Button
        variant="outline"
        onClick={() => setAuditDrawerOpen(true)}
      >
        View Full Audit Trail
      </Button>
    </div>

    {/* Override Modal */}
    <OverrideModal
      isOpen={overrideModalOpen}
      onClose={() => setOverrideModalOpen(false)}
      workItem={workItem}
      currentAssignee={primaryHuman}
      onOverride={handleOverride}
    />

    {/* Audit Drawer */}
    <Drawer open={auditDrawerOpen} onOpenChange={setAuditDrawerOpen}>
      <DrawerContent className="bg-[#141414] border-[#1a1a1a]">
        <DrawerHeader>
          <DrawerTitle>Audit Trail</DrawerTitle>
          <DrawerDescription>
            Complete decision reasoning chain for {workItem.id}
          </DrawerDescription>
        </DrawerHeader>
        <DrawerContent>
          <AuditTrail workItemId={workItem.id} />
        </DrawerContent>
      </DrawerContent>
    </Drawer>
  </div>
</MainLayout>
```

---

## Complete Checklist

### Design System Foundation (Hour 1-2)
- [ ] Initialize Next.js 14 project with shadcn/ui
- [ ] Create design system tokens (colors, typography, spacing)
- [ ] Build base layout component
- [ ] Create typography scale
- [ ] Setup Tailwind config

### Service Scaffolding (Hour 2-3)
- [ ] Create base UI components (Button, Card, Badge, Table)
- [ ] Create layout structure (sidebar, main content)
- [ ] Add API client utilities (fetch with correlation IDs)
- [ ] Setup react-force-graph-3d
- [ ] Create KnowledgeGraph3D component
- [ ] Setup graph data fetching
- [ ] Setup filtering UI

### UI Foundation (Hour 12-16)
- [ ] Work Items List page
- [ ] Work Item Detail page
- [ ] Override workflow
- [ ] Stats display
- [ ] Knowledge Graph Visualization
- [ ] All API integrations

### UI Polish (Hour 24-28)
- [ ] Evidence display (collapsible, well-formatted)
- [ ] Constraints table (clear pass/fail indicators)
- [ ] Audit drawer (readable score breakdown)
- [ ] Override flow (smooth, clear feedback)
- [ ] Loading states, error states
- [ ] Responsive design

### UI Completion (Hour 44-48)
- [ ] All pages functional
- [ ] All API integrations working
- [ ] Override flow end-to-end
- [ ] Stats display
- [ ] Error handling
- [ ] Loading states

### Final Polish (Hour 64-68)
- [ ] Final design pass
- [ ] Ensure all text is clear and unambiguous
- [ ] Add tooltips/explaners where needed
- [ ] Test on different screen sizes
- [ ] Ensure loading/error states are polished

### Documentation
- [ ] Create `/apps/ui/README.md`
- [ ] Document design system
- [ ] Document all components
- [ ] Document API integration
- [ ] Document knowledge graph visualization

---

## Key Principles

1. **Opinionated design**: No ambiguity, no questions
2. **Evidence-first**: Decisions must be explainable
3. **Reversibility**: Override must be obvious and easy
4. **Trust**: Audit trail must be inspectable
5. **Visual understanding**: 3D graph shows patterns humans can't see

---

## Dependencies

- **Next.js 14** (App Router)
- **TypeScript**
- **shadcn/ui** (component library)
- **Tailwind CSS** (styling)
- **react-force-graph-3d** (3D graph visualization)
- **Ingest Service**: `GET /work-items`, `GET /work-items/:id`, `POST /work-items/:id/outcome`
- **Decision Service**: `GET /decisions/:work_item_id`, `GET /audit/:work_item_id`
- **Learner Service**: `GET /stats?human_id=X`
- **Graph Service** (or Decision): `GET /graph/nodes`

---

## Environment Variables

```bash
# UI
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_DECISION_URL=http://localhost:8002
NEXT_PUBLIC_LEARNER_URL=http://localhost:8003
NEXT_PUBLIC_GRAPH_URL=http://localhost:8002  # Or separate Graph service
```

---

## Success Criteria

- ✅ Can list work items with filtering
- ✅ Can view decision with evidence
- ✅ Can override (updates learner stats)
- ✅ Can view audit trace
- ✅ Design is clean, opinionated, no ambiguity
- ✅ Knowledge graph visualization works (3D interactive)
- ✅ All error states handled
- ✅ All loading states handled
- ✅ Responsive design works

---

## Why This Matters

**The UI is the Trust Layer:**
- **Visibility**: People need to see decisions and evidence
- **Reversibility**: Override is the learning signal
- **Trust**: Audit trail must be inspectable
- **Visual understanding**: 3D graph shows patterns humans can't see

**Without a good UI:**
- System is untrustworthy (can't see why decisions were made)
- Learning loop doesn't work (can't override)
- Demo fails (judges can't see the value)

Good luck. Build the window.

