/**
 * Sync current Clerk user to Postgres.
 * Called on first dashboard load to ensure user exists in DB.
 */

import { auth, currentUser } from '@clerk/nextjs/server'
import { upsertUser } from '@/lib/db'
import { NextResponse } from 'next/server'

export async function POST() {
  try {
    const { userId } = await auth()
    
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const user = await currentUser()
    
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    const displayName = [user.firstName, user.lastName].filter(Boolean).join(' ') || 'User'
    const email = user.emailAddresses.find(e => e.id === user.primaryEmailAddressId)?.emailAddress

    const dbUser = await upsertUser({
      id: userId,
      displayName,
      email,
    })

    return NextResponse.json({ success: true, user: dbUser })
  } catch (error) {
    console.error('Error syncing user:', error)
    return NextResponse.json({ error: 'Failed to sync user' }, { status: 500 })
  }
}
