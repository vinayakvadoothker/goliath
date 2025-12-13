import { CheckCircle2, Sparkles } from 'lucide-react';

export function SuccessScreen() {
  return (
    <div className="bg-[#020202] border border-[#262626] rounded-lg p-8 flex flex-col items-center justify-center min-h-[600px] relative overflow-hidden">
      {/* Subtle glow effect */}
      <div className="absolute inset-0 bg-gradient-radial from-white/5 to-transparent opacity-30"></div>
      
      <div className="relative z-10 text-center">
        <div className="mb-6 relative inline-block">
          <div className="absolute inset-0 bg-white/20 rounded-full blur-2xl"></div>
          <CheckCircle2 className="w-24 h-24 text-white relative z-10 animate-[scale-in_0.5s_ease-out]" strokeWidth={1.5} />
        </div>
        
        <div className="mb-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <h2 className="text-white">You're all set!</h2>
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <p className="text-[#d9d9d9] max-w-sm mx-auto">
            Your workspace is ready. Let's start managing incidents smarter with Centra.
          </p>
        </div>
        
        <div className="space-y-3 mb-8">
          <div className="flex items-center gap-3 text-[#d9d9d9] text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-[#00ff00] shadow-[0_0_8px_rgba(0,255,0,0.6)]"></div>
            <span>Workspace configured</span>
          </div>
          <div className="flex items-center gap-3 text-[#d9d9d9] text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-[#00ff00] shadow-[0_0_8px_rgba(0,255,0,0.6)]"></div>
            <span>Integrations connected</span>
          </div>
          <div className="flex items-center gap-3 text-[#d9d9d9] text-sm">
            <div className="w-1.5 h-1.5 rounded-full bg-[#00ff00] shadow-[0_0_8px_rgba(0,255,0,0.6)]"></div>
            <span>AI models initialized</span>
          </div>
        </div>
        
        <button className="bg-white text-black px-8 py-4 rounded-md hover:bg-[#f0f0f0] transition-all hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] group">
          <span className="inline-flex items-center gap-2">
            Enter Dashboard
            <svg 
              className="w-4 h-4 transition-transform group-hover:translate-x-1" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
        </button>
      </div>
    </div>
  );
}