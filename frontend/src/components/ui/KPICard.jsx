import React from 'react';

export const KPICard = ({ title, value, benchmark, status, statusText, subValue }) => {
  const getStatusColor = (st) => {
    switch (st?.toUpperCase()) {
      case 'CRITICAL':
      case 'FAIL':
      case 'RED':
        return 'bg-red-500/10 border-red-500/40 text-red-400';
      case 'CAUTION':
      case 'FLAGGED':
      case 'AMBER':
        return 'bg-amber-500/10 border-amber-500/40 text-amber-400';
      case 'HEALTHY':
      case 'PASS':
      case 'EXCELLENT':
      case 'GREEN':
      default:
        return 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400';
    }
  };

  const getBadgeColor = (st) => {
    switch (st?.toUpperCase()) {
      case 'CRITICAL':
      case 'FAIL':
      case 'RED':
        return 'bg-red-950 text-red-400 border-red-800';
      case 'CAUTION':
      case 'FLAGGED':
      case 'AMBER':
        return 'bg-amber-950 text-amber-400 border-amber-800';
      case 'HEALTHY':
      case 'PASS':
      case 'EXCELLENT':
      case 'GREEN':
      default:
        return 'bg-emerald-950 text-emerald-400 border-emerald-800';
    }
  };

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4 flex flex-col justify-between shadow-sm">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{title}</span>
        {statusText && (
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${getBadgeColor(status)}`}>
            {statusText}
          </span>
        )}
      </div>

      <div className="my-2">
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        {subValue && <div className="text-xs text-slate-400 mt-0.5">{subValue}</div>}
      </div>

      {benchmark && (
        <div className="text-[11px] text-slate-500 flex items-center justify-between pt-2 border-t border-slate-800/80">
          <span>Benchmark</span>
          <span className="text-slate-300 font-medium font-mono">{benchmark}</span>
        </div>
      )}
    </div>
  );
};

export const StatusBadge = ({ status }) => {
  const st = (status || 'PASS').toUpperCase();
  if (st === 'PASS' || st === 'HEALTHY' || st === 'CLEARED') {
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 inline-block font-mono">
        PASS
      </span>
    );
  }
  if (st === 'FLAGGED' || st === 'REVIEW REQUIRED' || st === 'CAUTION') {
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-950/80 text-amber-400 border border-amber-800/80 inline-block font-mono">
        FLAGGED
      </span>
    );
  }
  return (
    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950/80 text-red-400 border border-red-800/80 inline-block font-mono">
      FAIL
    </span>
  );
};
