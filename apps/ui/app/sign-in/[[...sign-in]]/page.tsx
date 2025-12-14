/**
 * Sign-in page using Clerk's pre-built SignIn component.
 * Centered layout with dark theme matching the app design.
 */

import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <img src="/logo.png" alt="Centra Logo" className="h-12 w-12" />
            <h1 className="text-3xl font-bold text-white">Centra</h1>
          </div>
          <p className="text-gray-400">Sign in to your account</p>
        </div>
        <SignIn
          fallbackRedirectUrl="/dashboard"
          appearance={{
            elements: {
              rootBox: 'w-full',
              card: 'bg-[#1a1a1a] border border-[#333] shadow-xl',
            },
          }}
        />
      </div>
    </div>
  )
}
