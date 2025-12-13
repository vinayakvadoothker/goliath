export function IntegrationsScreen() {
  return (
    <div className="bg-[#020202] border border-[#262626] rounded-lg p-8 flex flex-col justify-center min-h-[600px]">
      <div className="w-full">
        <h2 className="text-white mb-2">Connect incident reporting</h2>
        <p className="text-[#666] mb-8 text-sm">Where do your alerts come from?</p>
        
        <div className="space-y-3">
          {/* DataDog */}
          <div className="bg-[#0a0a0a] border border-[#262626] rounded-lg p-4 hover:border-white transition-colors cursor-pointer group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#632CA6] rounded-lg flex items-center justify-center p-2.5">
                  <svg viewBox="0 0 71 67" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                    <path d="M35.5 36.5h-8v16h8v-16z" fill="white"/>
                    <path d="M23.5 41.5h-8v11h8v-11z" fill="white" opacity="0.7"/>
                    <path d="M47.5 41.5h-8v11h8v-11z" fill="white" opacity="0.7"/>
                    <ellipse cx="35.5" cy="20" rx="6" ry="6" fill="white"/>
                    <ellipse cx="13" cy="32" rx="2.5" ry="2.5" fill="white" opacity="0.6"/>
                    <ellipse cx="58" cy="32" rx="2.5" ry="2.5" fill="white" opacity="0.6"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-white mb-1">Datadog</h3>
                  <p className="text-[#666] text-xs">Monitor and alert on infrastructure metrics</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-[#00ff00] shadow-[0_0_8px_rgba(0,255,0,0.6)]"></div>
                <span className="text-[#00ff00] text-xs">Connected</span>
              </div>
            </div>
          </div>
          
          {/* PagerDuty */}
          <div className="bg-[#0a0a0a] border border-[#262626] rounded-lg p-4 hover:border-white transition-colors cursor-pointer group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#06AC38] rounded-lg flex items-center justify-center p-2.5">
                  <svg viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                    <path d="M144 96h80c44.2 0 80 35.8 80 80v0c0 44.2-35.8 80-80 80h-80V96z" fill="white"/>
                    <path d="M144 256h160v48H144v-48z" fill="white"/>
                    <path d="M144 336h160v48H144v-48z" fill="white"/>
                    <rect x="144" y="96" width="80" height="160" stroke="white" strokeWidth="12" fill="none"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-white mb-1">PagerDuty</h3>
                  <p className="text-[#666] text-xs">On-call scheduling and incident response</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-[#00ff00] shadow-[0_0_8px_rgba(0,255,0,0.6)]"></div>
                <span className="text-[#00ff00] text-xs">Connected</span>
              </div>
            </div>
          </div>
          
          {/* AWS CloudWatch */}
          <div className="bg-[#0a0a0a] border border-[#262626] rounded-lg p-4 hover:border-white transition-colors cursor-pointer group">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-[#FF9900] rounded-lg flex items-center justify-center p-2.5">
                  <svg viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                    <path d="M70 180L128 145L186 180L128 215L70 180z" fill="#232F3E"/>
                    <path d="M128 145V75L70 110V180L128 145z" fill="#232F3E" opacity="0.7"/>
                    <path d="M128 145V75L186 110V180L128 145z" fill="#232F3E" opacity="0.9"/>
                    <path d="M186 110L128 75L70 110" stroke="white" strokeWidth="4"/>
                    <path d="M70 145L128 110L186 145M70 180L128 145L186 180" stroke="white" strokeWidth="3" opacity="0.8"/>
                  </svg>
                </div>
                <div>
                  <h3 className="text-white mb-1">AWS CloudWatch</h3>
                  <p className="text-[#666] text-xs">Monitor AWS resources and applications</p>
                </div>
              </div>
              <button className="border border-[#262626] text-white px-4 py-2 rounded-md text-sm hover:border-white hover:bg-white hover:text-black transition-colors">
                Connect
              </button>
            </div>
          </div>
        </div>
        
        <button className="w-full bg-white text-black py-3 rounded-md mt-8 hover:bg-[#f0f0f0] transition-colors">
          Continue
        </button>
      </div>
    </div>
  );
}