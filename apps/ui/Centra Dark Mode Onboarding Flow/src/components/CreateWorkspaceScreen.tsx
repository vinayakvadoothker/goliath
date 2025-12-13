import { Building2, Upload } from 'lucide-react';

export function CreateWorkspaceScreen() {
  return (
    <div className="bg-[#020202] border border-[#262626] rounded-lg p-8 flex flex-col justify-center min-h-[600px]">
      <div className="w-full max-w-sm mx-auto">
        <h2 className="text-white mb-2">Name your workspace</h2>
        <p className="text-[#666] mb-8 text-sm">This will be your team's home in Centra</p>
        
        <div className="space-y-6">
          <div>
            <label className="text-[#d9d9d9] text-sm mb-2 block">Organization Name</label>
            <input
              type="text"
              defaultValue="Acme Corp"
              className="w-full bg-[#0a0a0a] border border-[#262626] text-white px-4 py-3 rounded-md outline-none focus:border-white transition-colors"
            />
          </div>
          
          <div>
            <label className="text-[#d9d9d9] text-sm mb-2 block">Organization Logo</label>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-[#0a0a0a] border border-[#262626] flex items-center justify-center text-white text-xl">
                A
              </div>
              <div className="flex-1">
                <p className="text-[#d9d9d9] text-sm mb-1">Upload your logo</p>
                <p className="text-[#666] text-xs">PNG, JPG or SVG (max. 2MB)</p>
              </div>
            </div>
          </div>
          
          <div>
            <label className="text-[#d9d9d9] text-sm mb-2 block">Your Workspace URL</label>
            <div className="bg-[#0a0a0a] border border-[#262626] px-4 py-3 rounded-md">
              <p className="text-[#666] text-sm">centra.ai/<span className="text-white">acme-corp</span></p>
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