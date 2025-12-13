import { Key, Link2 } from 'lucide-react';

export function JiraConnectionScreen() {
  return (
    <div className="bg-[#020202] border border-[#262626] rounded-lg p-8 flex flex-col justify-center min-h-[600px]">
      <div className="w-full max-w-sm mx-auto">
        <h2 className="text-white mb-2">Connect issue tracking</h2>
        <p className="text-[#666] mb-8 text-sm">Sync with your project management</p>
        
        <div className="mb-8">
          <div className="w-20 h-20 bg-[#0052CC] rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <path d="M24 12L12 24L24 36L36 24L24 12Z" fill="white"/>
              <path d="M24 18L18 24L24 30L30 24L24 18Z" fill="#0052CC"/>
            </svg>
          </div>
          <h3 className="text-white text-center mb-1">Jira</h3>
          <p className="text-[#666] text-center text-sm">Connect your Jira workspace</p>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="text-[#d9d9d9] text-sm mb-2 block">Jira Domain URL</label>
            <div className="relative">
              <Link2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#666]" />
              <input
                type="text"
                placeholder="your-domain.atlassian.net"
                className="w-full bg-[#0a0a0a] border border-[#262626] text-white pl-10 pr-4 py-3 rounded-md outline-none focus:border-white transition-colors placeholder:text-[#666]"
              />
            </div>
          </div>
          
          <div>
            <label className="text-[#d9d9d9] text-sm mb-2 block">API Token</label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#666]" />
              <input
                type="password"
                placeholder="Enter your API token"
                className="w-full bg-[#0a0a0a] border border-[#262626] text-white pl-10 pr-4 py-3 rounded-md outline-none focus:border-white transition-colors placeholder:text-[#666]"
              />
            </div>
            <p className="text-[#666] text-xs mt-2">
              <a href="#" className="text-white hover:underline">Generate an API token</a> in your Jira settings
            </p>
          </div>
        </div>
        
        <button className="w-full bg-white text-black py-3 rounded-md mt-6 hover:bg-[#f0f0f0] transition-colors">
          Authorize Jira
        </button>
        
        <div className="mt-6 pt-6 border-t border-[#262626]">
          <p className="text-[#666] text-xs text-center mb-3">Also available:</p>
          <div className="flex justify-center gap-4">
            <div className="w-10 h-10 bg-[#0a0a0a] border border-[#262626] rounded-lg flex items-center justify-center cursor-pointer hover:border-white transition-colors">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#5E6AD2"/>
                <path d="M2 17L12 22L22 17" stroke="#5E6AD2" strokeWidth="2"/>
              </svg>
            </div>
            <div className="w-10 h-10 bg-[#0a0a0a] border border-[#262626] rounded-lg flex items-center justify-center cursor-pointer hover:border-white transition-colors">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
