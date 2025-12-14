/**
 * Sync current user to Postgres.
 * Called on first dashboard load to ensure user exists in DB.
 */

import { NextResponse } from 'next/server'

export async function POST() {
  // Clerk removed - return success for now
  return NextResponse.json({ success: true, message: 'User sync disabled' })
}
