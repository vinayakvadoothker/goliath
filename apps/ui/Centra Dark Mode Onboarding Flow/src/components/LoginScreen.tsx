import { Mail, Lock, Github } from 'lucide-react';
import { CentraLogo } from './CentraLogo';

export function LoginScreen() {
  return (
    <div className="bg-[#020202] border border-[#262626] rounded-lg p-8 flex flex-col items-center justify-center min-h-[600px]">
      <div className="w-full max-w-sm">
        <div className="flex justify-center mb-8">
          <CentraLogo />
        </div>
        
        <h2 className="text-white text-center mb-8">Welcome back</h2>
        
        <div className="space-y-4 mb-6">
          <div className="relative">
            <Mail className="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-4 text-[#666]" />
            <input
              type="email"
              placeholder="Email address"
              className="w-full bg-transparent border-b border-[#262626] text-[#d9d9d9] pl-6 pb-2 outline-none focus:border-white transition-colors placeholder:text-[#666]"
            />
          </div>
          
          <div className="relative">
            <Lock className="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-4 text-[#666]" />
            <input
              type="password"
              placeholder="Password"
              className="w-full bg-transparent border-b border-[#262626] text-[#d9d9d9] pl-6 pb-2 outline-none focus:border-white transition-colors placeholder:text-[#666]"
            />
          </div>
        </div>
        
        <button className="w-full bg-white text-black py-3 rounded-md mb-4 hover:bg-[#f0f0f0] transition-colors">
          Sign In
        </button>
        
        <div className="space-y-2">
          <button className="w-full border border-[#262626] text-white py-3 rounded-md hover:border-white transition-colors flex items-center justify-center gap-2">
            <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Sign in with Google
          </button>
          
          <button className="w-full border border-[#262626] text-white py-3 rounded-md hover:border-white transition-colors flex items-center justify-center gap-2">
            <Github className="w-5 h-5" />
            Sign in with GitHub
          </button>
        </div>
        
        <p className="text-[#666] text-center mt-6 text-sm">
          Don't have an account? <span className="text-white cursor-pointer hover:underline">Sign up</span>
        </p>
      </div>
    </div>
  );
}
