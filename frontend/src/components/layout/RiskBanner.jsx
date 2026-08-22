import React from 'react';
import { AlertTriangle, ShieldAlert, X } from 'lucide-react';
import { useEngagementStore } from '../../stores/useEngagementStore';

export const RiskBanner = () => {
  const { riskBanner, setRiskBanner } = useEngagementStore();

  if (!riskBanner.active) return null;

  return (
    <div className="bg-gradient-to-r from-red-900/90 via-red-950 to-amber-950 border-b border-red-500/40 text-white px-4 py-2.5 shadow-lg flex items-center justify-between text-xs tracking-wide sticky top-0 z-50 backdrop-blur-md animate-pulse">
      <div className="flex items-center space-x-3">
        <div className="p-1 bg-red-500/20 rounded border border-red-500/40">
          <ShieldAlert className="w-4 h-4 text-red-400" />
        </div>
        <div>
          <span className="font-bold text-red-300 mr-2 uppercase tracking-wider">High Risk Audit Waiver Warning:</span>
          <span className="text-slate-200">{riskBanner.message}</span>
        </div>
      </div>
      <div className="flex items-center space-x-3">
        <span className="px-2 py-0.5 rounded bg-red-500/30 text-red-200 border border-red-500/50 font-mono text-[10px]">
          WAIVED_RISK_ACTIVE
        </span>
        <button
          onClick={() => setRiskBanner(false)}
          className="text-slate-400 hover:text-white transition p-1 hover:bg-slate-800 rounded"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
