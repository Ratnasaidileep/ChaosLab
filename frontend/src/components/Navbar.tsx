import React from 'react';
import {
  Activity,
  Layers,
  Flame,
  History,
  BarChart3,
  ExternalLink,
  ShieldCheck,
  Server
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemHealth: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  systemHealth,
}) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'services', label: 'Service Health', icon: Server },
    { id: 'injection', label: 'Failure Injection', icon: Flame },
    { id: 'history', label: 'Experiment History', icon: History },
    { id: 'analysis', label: 'Recovery Analysis', icon: BarChart3 },
  ];

  const getHealthBadge = () => {
    switch (systemHealth) {
      case 'HEALTHY':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            SYSTEM RESILIENT
          </span>
        );
      case 'DEGRADED':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            SYSTEM DEGRADED
          </span>
        );
      case 'UNHEALTHY':
        return (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <span className="w-2 h-2 rounded-full bg-rose-400 animate-pulse"></span>
            FAILURE DETECTED
          </span>
        );
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-[#0B1120]/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white">
                  Chaos<span className="text-cyan-400">Lab</span>
                </span>
                <span className="text-[10px] font-mono tracking-wider uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  DevOps Platform
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Automated Failure Injection & Recovery</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {/* Right Tools & Status */}
          <div className="flex items-center gap-3">
            {getHealthBadge()}

            <div className="hidden lg:flex items-center gap-1 border-l border-slate-800 pl-3">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                title="FastAPI Swagger Documentation"
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-mono text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 rounded transition"
              >
                API Docs
                <ExternalLink className="w-3 h-3" />
              </a>
              <a
                href="http://localhost:9090"
                target="_blank"
                rel="noreferrer"
                title="Prometheus Metrics"
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-mono text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 rounded transition"
              >
                Prometheus
                <ExternalLink className="w-3 h-3" />
              </a>
              <a
                href="http://localhost:3001"
                target="_blank"
                rel="noreferrer"
                title="Grafana Dashboard (admin/chaoslab)"
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-mono text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 rounded transition"
              >
                Grafana
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="flex md:hidden overflow-x-auto py-2 space-x-2 border-t border-slate-800/60 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200 bg-slate-800/40'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
