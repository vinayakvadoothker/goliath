/**
 * Sign-up page using Clerk's pre-built SignUp component.
 * Centered layout with dark theme matching the app design.
 */

import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <img src="/logo.png" alt="Centra Logo" className="h-12 w-12" />
            <h1 className="text-3xl font-bold text-white">Centra</h1>
          </div>
          <p className="text-gray-400">Create your account</p>
        </div>
        <SignUp
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
