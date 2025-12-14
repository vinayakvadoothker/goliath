# Goliath UI

**Evidence-first interface - Next.js 14 with TypeScript and shadcn/ui.**

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment variables (see below)
cp .env.local.example .env.local

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Authentication

This app uses [Clerk](https://clerk.com) for authentication. To set up:

1. Create a Clerk account at https://clerk.com
2. Create a new application
3. Copy your API keys to `.env.local`

## Pages

### Public Routes
- `/` - Landing page
- `/sign-in` - Sign in page (OAuth)
- `/sign-up` - Sign up page (OAuth)

### Protected Routes (require authentication)
- `/dashboard` - Main dashboard
- `/work-items` - Work Items List
- `/work-items/[id]` - Work Item Detail
- `/graph` - Knowledge Graph 3D Visualization
- `/stats` - Human Stats

## Environment Variables

Create a `.env.local` file with:

```bash
# Clerk Authentication (required)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here
CLERK_WEBHOOK_SECRET=whsec_your_webhook_secret  # For user sync to Postgres

# Clerk URLs (optional - these are the defaults)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Database (for user sync)
DATABASE_URL=postgresql://goliath:goliath@localhost:5432/goliath

# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_DECISION_URL=http://localhost:8002
NEXT_PUBLIC_LEARNER_URL=http://localhost:8003
NEXT_PUBLIC_GRAPH_URL=http://localhost:8002
```

## User Sync to Postgres

Users are automatically synced to the `humans` table in Postgres when they first access authenticated pages (no webhook setup needed for local dev).

### Production Webhook Setup (Optional)

For real-time sync in production:

1. Go to Clerk Dashboard → Webhooks
2. Create endpoint: `https://your-domain/api/webhooks/clerk`
3. Subscribe to: `user.created`, `user.updated`, `user.deleted`
4. Copy the signing secret to `CLERK_WEBHOOK_SECRET`

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

