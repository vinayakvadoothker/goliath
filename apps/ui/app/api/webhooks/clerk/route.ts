/**
 * Clerk webhook handler (disabled).
 * Syncs user data to Postgres on user.created, user.updated, user.deleted events.
 */

import { NextResponse } from 'next/server'

export async function POST() {
  // Clerk removed - return success for now
  return NextResponse.json({ success: true, message: 'Webhook disabled' })
}
