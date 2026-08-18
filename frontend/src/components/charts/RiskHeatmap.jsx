import React from 'react';

export const RiskHeatmap = () => {
  return (
    <div className="flex flex-col items-center">
      <div className="flex items-center space-x-2 text-[10px] text-slate-400 mb-1">
        <span>Inherent vs Control Risk</span>
      </div>
      <div className="grid grid-cols-3 gap-1.5 p-2 bg-[#0B1120] border border-[#1E293B] rounded-lg">
        {/* Row 1 (High Inherent) */}
        <div className="w-9 h-7 rounded bg-amber-500/60 flex items-center justify-center text-[10px] font-bold text-black">
          Med
        </div>
        <div className="w-9 h-7 rounded bg-red-500/80 flex items-center justify-center text-[10px] font-bold text-white shadow-sm ring-1 ring-red-400">
          High
        </div>
        <div className="w-9 h-7 rounded bg-red-600 flex items-center justify-center text-[10px] font-bold text-white">
          Crit
        </div>

        {/* Row 2 (Med Inherent) */}
        <div className="w-9 h-7 rounded bg-emerald-500/50 flex items-center justify-center text-[10px] font-bold text-white">
          Low
        </div>
        <div className="w-9 h-7 rounded bg-amber-500/70 flex items-center justify-center text-[10px] font-bold text-black">
          Med
        </div>
        <div className="w-9 h-7 rounded bg-red-500/80 flex items-center justify-center text-[10px] font-bold text-white">
          High
        </div>

        {/* Row 3 (Low Inherent) */}
        <div className="w-9 h-7 rounded bg-emerald-600 flex items-center justify-center text-[10px] font-bold text-white">
          Low
        </div>
        <div className="w-9 h-7 rounded bg-emerald-500/50 flex items-center justify-center text-[10px] font-bold text-white">
          Low
        </div>
        <div className="w-9 h-7 rounded bg-amber-500/60 flex items-center justify-center text-[10px] font-bold text-black">
          Med
        </div>
      </div>
      <div className="flex justify-between w-full text-[9px] text-slate-500 mt-1 px-1">
        <span>Low</span>
        <span>Control Risk</span>
        <span>High</span>
      </div>
    </div>
  );
};
