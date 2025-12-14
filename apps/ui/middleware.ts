/**
 * Clerk middleware for route protection.
 * Protects all routes except public ones.
 * Redirects signed-in users from public pages to dashboard.
 */

import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/health(.*)',
  '/api/webhooks(.*)',
  '/api/user(.*)',
])

const isAuthRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  const { userId } = await auth()

  // If signed in and on landing/auth pages, redirect to dashboard
  if (userId && isAuthRoute(req)) {
    const dashboardUrl = new URL('/dashboard', req.url)
    return NextResponse.redirect(dashboardUrl)
  }

  // Protect non-public routes
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
