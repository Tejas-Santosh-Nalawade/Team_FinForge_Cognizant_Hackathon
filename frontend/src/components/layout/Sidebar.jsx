import React from 'react';
import {
  LayoutDashboard,
  Database,
  TrendingUp,
  FileSpreadsheet,
  Flag,
  Sliders,
  FileText,
  CheckSquare,
  Settings,
  ShieldAlert
} from 'lucide-react';
import { useEngagementStore } from '../../stores/useEngagementStore';

export const Sidebar = () => {
  const { activeTab, setActiveTab, riskBanner } = useEngagementStore();

  const navItems = [
    { id: 'planning', label: 'Planning', icon: LayoutDashboard },
    { id: 'ingestion', label: 'Ingestion', icon: Database },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'execution', label: 'Audit Suite', icon: FileSpreadsheet },
    { id: 'findings', label: 'Findings', icon: Flag },
    { id: 'simulator', label: 'Simulator', icon: Sliders },
    { id: 'reporting', label: 'Reports', icon: FileText },
    { id: 'closure', label: 'Closure', icon: CheckSquare },
  ];

  return (
    <aside className="w-16 bg-[#0F172A] border-r border-[#1E293B] flex flex-col items-center py-4 space-y-6 select-none shrink-0">
      <div className="w-10 h-10 rounded-lg bg-sky-600/20 border border-sky-500/40 flex items-center justify-center text-sky-400 font-bold text-sm">
        WP
      </div>

      <nav className="flex-1 flex flex-col space-y-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              title={item.label}
              className={`p-2.5 rounded-xl transition cursor-pointer relative group flex items-center justify-center ${
                isActive
                  ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="absolute left-16 bg-slate-900 border border-slate-700 text-white text-xs font-semibold px-2 py-1 rounded-md opacity-0 pointer-events-none group-hover:opacity-100 transition whitespace-nowrap z-50 shadow-xl">
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>

      {riskBanner.active && (
        <div title="Waiver Active" className="p-2 rounded-xl bg-red-950/60 border border-red-500/50 text-red-400 animate-pulse">
          <ShieldAlert className="w-5 h-5" />
        </div>
      )}

      <div className="pt-4 border-t border-slate-800">
        <button
          onClick={() => setActiveTab('reporting')}
          title="Settings & Parameters"
          className="p-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition cursor-pointer"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </aside>
  );
};
