/**
 * Sign-in page (Clerk removed).
 */

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <img src="/logo.png" alt="Goliath Logo" className="h-12 w-12" />
            <h1 className="text-3xl font-bold text-white">Goliath</h1>
          </div>
          <p className="text-gray-400">Sign in to your account</p>
          <p className="text-gray-500 mt-4">Authentication is currently disabled</p>
        </div>
      </div>
    </div>
  )
}
