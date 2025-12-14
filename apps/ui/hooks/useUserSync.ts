/**
 * Hook to sync Clerk user to Postgres on first load.
 * Only runs once per session.
 */

'use client'

import { useEffect, useRef } from 'react'
import { useUser } from '@clerk/nextjs'

export function useUserSync() {
  const { isSignedIn, user } = useUser()
  const hasSynced = useRef(false)

  useEffect(() => {
    if (isSignedIn && user && !hasSynced.current) {
      hasSynced.current = true
      
      fetch('/api/user/sync', { method: 'POST' })
        .then(res => {
          if (!res.ok) console.error('Failed to sync user to database')
        })
        .catch(err => console.error('Error syncing user:', err))
    }
  }, [isSignedIn, user])
}
