import { Check } from 'lucide-react';

export function PricingScreen() {
  return (
    <div className="bg-[#020202] border border-[#262626] rounded-lg p-8 flex flex-col justify-center min-h-[600px]">
      <div className="w-full max-w-md mx-auto">
        <h2 className="text-white text-center mb-2">Select your plan</h2>
        <p className="text-[#666] text-center mb-6 text-sm">Choose the perfect plan for your team</p>
        
        <div className="space-y-4">
          {/* Starter */}
          <div className="border border-[#262626] rounded-lg p-4 hover:border-[#404040] transition-colors">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-white mb-1">Starter</h3>
                <div>
                  <span className="text-white text-2xl">$0</span>
                  <span className="text-[#666] text-sm">/mo</span>
                </div>
              </div>
              <button className="border border-[#262626] text-white px-4 py-1.5 rounded-md text-xs hover:border-white transition-colors">
                Get Started
              </button>
            </div>
            
            <ul className="space-y-1.5">
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>Up to 5 users</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>Basic integrations</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>Community support</span>
              </li>
            </ul>
          </div>
          
          {/* Pro */}
          <div className="border-2 border-white rounded-lg p-4 relative shadow-[0_0_30px_rgba(255,255,255,0.1)]">
            <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-white text-black px-3 py-0.5 rounded-full text-xs">
              Recommended
            </div>
            
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-white mb-1">Pro</h3>
                <div>
                  <span className="text-white text-2xl">$29</span>
                  <span className="text-[#666] text-sm">/user/mo</span>
                </div>
              </div>
              <button className="bg-white text-black px-4 py-1.5 rounded-md text-xs hover:bg-[#f0f0f0] transition-colors">
                Start Trial
              </button>
            </div>
            
            <ul className="space-y-1.5">
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-white mt-0.5 flex-shrink-0" />
                <span>Unlimited users</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-white mt-0.5 flex-shrink-0" />
                <span>Advanced integrations</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-white mt-0.5 flex-shrink-0" />
                <span>Priority support</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-white mt-0.5 flex-shrink-0" />
                <span>AI incident analysis</span>
              </li>
            </ul>
          </div>
          
          {/* Enterprise */}
          <div className="border border-[#262626] rounded-lg p-4 hover:border-[#404040] transition-colors">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-white mb-1">Enterprise</h3>
                <div>
                  <span className="text-white text-lg">Custom</span>
                </div>
              </div>
              <button className="border border-[#262626] text-white px-4 py-1.5 rounded-md text-xs hover:border-white transition-colors">
                Contact Us
              </button>
            </div>
            
            <ul className="space-y-1.5">
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>Custom deployment</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>SLA guarantee</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>Dedicated support</span>
              </li>
              <li className="flex items-start gap-2 text-[#d9d9d9] text-xs">
                <Check className="w-3.5 h-3.5 text-[#666] mt-0.5 flex-shrink-0" />
                <span>Custom integrations</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}