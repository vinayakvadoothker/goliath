# Goliath Control Center

Interactive incident simulation and routing demo - a standalone Next.js application that lets you trigger errors and watch Goliath route them in real-time.

## Quick Start

```bash
# Install dependencies
pnpm install

# Run development server (runs on port 6767)
pnpm dev

# Build for production
pnpm build

# Start production server (runs on port 6767)
pnpm start
```

The Control Center runs on **port 6767** by default.

## Features

- **Interactive Error Triggers**: Click buttons to trigger different error types
- **Real-Time Updates**: WebSocket connection for live updates
- **Full Goliath Integration**: Watch incidents flow through Ingest → Decision → Executor
- **Visual Dashboard**: System health, metrics, logs, incidents, and decisions

## Environment Variables

```bash
NEXT_PUBLIC_WS_URL=ws://localhost:8007/ws
```

## Architecture

- **Frontend**: Next.js 14 + shadcn/ui + WebSocket client
- **Backend**: FastAPI + WebSocket server
- **Integration**: Connects to Ingest, Decision, and Executor services

## Color Palette

- Primary: `#9BB4C0` (Light Blue-Gray)
- Secondary: `#A18D6D` (Brown/Tan)
- Error: `#703B3B` (Dark Red/Burgundy)
- Background: `#E1D0B3` (Beige/Cream)
