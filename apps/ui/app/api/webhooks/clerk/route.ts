/**
 * Clerk webhook handler.
 * Syncs user data to Postgres on user.created, user.updated, user.deleted events.
 */

import { Webhook } from 'svix'
import { headers } from 'next/headers'
import { WebhookEvent } from '@clerk/nextjs/server'
import { upsertUser, deleteUser } from '@/lib/db'

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET

  if (!WEBHOOK_SECRET) {
    console.error('Missing CLERK_WEBHOOK_SECRET environment variable')
    return new Response('Webhook secret not configured', { status: 500 })
  }

  const headerPayload = await headers()
  const svix_id = headerPayload.get('svix-id')
  const svix_timestamp = headerPayload.get('svix-timestamp')
  const svix_signature = headerPayload.get('svix-signature')

  if (!svix_id || !svix_timestamp || !svix_signature) {
    return new Response('Missing svix headers', { status: 400 })
  }

  const payload = await req.json()
  const body = JSON.stringify(payload)

  const wh = new Webhook(WEBHOOK_SECRET)
  let evt: WebhookEvent

  try {
    evt = wh.verify(body, {
      'svix-id': svix_id,
      'svix-timestamp': svix_timestamp,
      'svix-signature': svix_signature,
    }) as WebhookEvent
  } catch (err) {
    console.error('Webhook verification failed:', err)
    return new Response('Invalid signature', { status: 400 })
  }

  const eventType = evt.type

  try {
    if (eventType === 'user.created' || eventType === 'user.updated') {
      const { id, first_name, last_name, email_addresses } = evt.data
      const displayName = [first_name, last_name].filter(Boolean).join(' ') || 'User'
      const primaryEmail = email_addresses?.find((e: { id: string }) => e.id === evt.data.primary_email_address_id)

      await upsertUser({
        id,
        displayName,
        email: primaryEmail?.email_address,
      })

      console.log(`User ${eventType === 'user.created' ? 'created' : 'updated'}: ${id}`)
    }

    if (eventType === 'user.deleted') {
      const { id } = evt.data
      if (id) {
        await deleteUser(id)
        console.log(`User deleted: ${id}`)
      }
    }

    return new Response('OK', { status: 200 })
  } catch (error) {
    console.error('Error processing webhook:', error)
    return new Response('Error processing webhook', { status: 500 })
  }
}
