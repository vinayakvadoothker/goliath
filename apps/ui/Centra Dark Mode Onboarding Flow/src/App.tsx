import { useState } from 'react';
import { LoginScreen } from './components/LoginScreen';
import { CreateWorkspaceScreen } from './components/CreateWorkspaceScreen';
import { PricingScreen } from './components/PricingScreen';
import { IntegrationsScreen } from './components/IntegrationsScreen';
import { JiraConnectionScreen } from './components/JiraConnectionScreen';
import { SuccessScreen } from './components/SuccessScreen';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const screens = [
  { component: LoginScreen, title: 'Sign In' },
  { component: CreateWorkspaceScreen, title: 'Create Workspace' },
  { component: PricingScreen, title: 'Select Plan' },
  { component: IntegrationsScreen, title: 'Connect Integrations' },
  { component: JiraConnectionScreen, title: 'Connect Jira' },
  { component: SuccessScreen, title: 'Success' },
];

export default function App() {
  const [currentScreen, setCurrentScreen] = useState(0);
  
  const CurrentComponent = screens[currentScreen].component;
  
  const goNext = () => {
    if (currentScreen < screens.length - 1) {
      setCurrentScreen(currentScreen + 1);
    }
  };
  
  const goPrev = () => {
    if (currentScreen > 0) {
      setCurrentScreen(currentScreen - 1);
    }
  };
  
  return (
    <div className="min-h-screen bg-[#020202] flex flex-col">
      {/* Navigation Header */}
      <div className="border-b border-[#262626] p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={goPrev}
              disabled={currentScreen === 0}
              className="p-2 text-white disabled:text-[#666] disabled:cursor-not-allowed hover:bg-[#0a0a0a] rounded-md transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-white text-sm">
              {currentScreen + 1} / {screens.length}
            </span>
            <button
              onClick={goNext}
              disabled={currentScreen === screens.length - 1}
              className="p-2 text-white disabled:text-[#666] disabled:cursor-not-allowed hover:bg-[#0a0a0a] rounded-md transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          
          <h1 className="text-white text-sm">{screens[currentScreen].title}</h1>
          
          <div className="flex gap-2">
            {screens.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentScreen(index)}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index === currentScreen ? 'bg-white' : 'bg-[#262626] hover:bg-[#404040]'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-2xl">
          <CurrentComponent />
        </div>
      </div>
    </div>
  );
}
