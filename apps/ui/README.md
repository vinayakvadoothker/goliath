# Goliath UI

**Evidence-first interface - Next.js 14 with TypeScript and shadcn/ui.**

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Pages

- `/` - Dashboard
- `/work-items` - Work Items List
- `/work-items/[id]` - Work Item Detail
- `/graph` - Knowledge Graph 3D Visualization
- `/stats/[human_id]` - Human Stats

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_DECISION_URL=http://localhost:8002
NEXT_PUBLIC_LEARNER_URL=http://localhost:8003
NEXT_PUBLIC_GRAPH_URL=http://localhost:8002
```

## Development

```bash
# Run with hot reload
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Test
npm run test
```

## Documentation

See [Person 5 Developer Guide](../../for_developer_docs/person5_ui.md) for complete documentation.

