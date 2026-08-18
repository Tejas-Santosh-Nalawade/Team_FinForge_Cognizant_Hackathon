import React from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import { CashBurnChart } from '../components/charts/CashBurnChart';
import { Sliders, RefreshCw, AlertTriangle, TrendingDown, DollarSign, Calendar } from 'lucide-react';

export const SimulatorDashboard = () => {
  const { simulator, updateSimulator } = useEngagementStore();

  const handleSliderChange = (key, value) => {
    updateSimulator({ [key]: parseFloat(value) });
  };

  const handleReset = () => {
    updateSimulator({
      salesVolumeDeltaPct: 0.0,
      pricingDeltaPct: 0.0,
      interestRateDeltaPct: 0.0,
      operatingCostsDeltaPct: 0.0,
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Title & Subheading */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-sky-400" />
            <span>What-If Scenario &amp; Stress-Test Simulator</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time sensitivity modeling across sales volumes, unit pricing, interest rate shocks, and operational cost curves.
          </p>
        </div>

        <button
          onClick={handleReset}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset to Baseline</span>
        </button>
      </div>

      {/* Main Grid: Left Sliders, Right 12-Month Curve */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 cols): Dynamic Driver Sliders */}
        <div className="lg:col-span-5 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-5">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Scenario Driver Controls</h3>

          {/* Slider 1: Sales Volume */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Sales Volume Shock</span>
              <span className={`font-mono font-bold ${simulator.salesVolumeDeltaPct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {simulator.salesVolumeDeltaPct >= 0 ? `+${simulator.salesVolumeDeltaPct}%` : `${simulator.salesVolumeDeltaPct}%`}
              </span>
            </div>
            <input
              type="range"
              min="-20"
              max="20"
              step="1"
              value={simulator.salesVolumeDeltaPct}
              onChange={(e) => handleSliderChange('salesVolumeDeltaPct', e.target.value)}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-20%</span>
              <span>Baseline (0%)</span>
              <span>+20%</span>
            </div>
          </div>

          {/* Slider 2: Pricing */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Unit Pricing Adjustment</span>
              <span className={`font-mono font-bold ${simulator.pricingDeltaPct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {simulator.pricingDeltaPct >= 0 ? `+${simulator.pricingDeltaPct}%` : `${simulator.pricingDeltaPct}%`}
              </span>
            </div>
            <input
              type="range"
              min="-15"
              max="15"
              step="1"
              value={simulator.pricingDeltaPct}
              onChange={(e) => handleSliderChange('pricingDeltaPct', e.target.value)}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-15%</span>
              <span>Baseline (0%)</span>
              <span>+15%</span>
            </div>
          </div>

          {/* Slider 3: Interest Rates */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Interest Rate Shock (Borrowing Costs)</span>
              <span className={`font-mono font-bold ${simulator.interestRateDeltaPct > 0 ? 'text-amber-400' : 'text-slate-300'}`}>
                {simulator.interestRateDeltaPct >= 0 ? `+${simulator.interestRateDeltaPct}%` : `${simulator.interestRateDeltaPct}%`}
              </span>
            </div>
            <input
              type="range"
              min="-5"
              max="25"
              step="1"
              value={simulator.interestRateDeltaPct}
              onChange={(e) => handleSliderChange('interestRateDeltaPct', e.target.value)}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-5%</span>
              <span>Baseline (0%)</span>
              <span>+25%</span>
            </div>
          </div>

          {/* Slider 4: Operating Costs */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Operating Costs Inflation / Scaling</span>
              <span className={`font-mono font-bold ${simulator.operatingCostsDeltaPct > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                {simulator.operatingCostsDeltaPct >= 0 ? `+${simulator.operatingCostsDeltaPct}%` : `${simulator.operatingCostsDeltaPct}%`}
              </span>
            </div>
            <input
              type="range"
              min="-10"
              max="60"
              step="5"
              value={simulator.operatingCostsDeltaPct}
              onChange={(e) => handleSliderChange('operatingCostsDeltaPct', e.target.value)}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>-10%</span>
              <span>Baseline (0%)</span>
              <span>+60%</span>
            </div>
          </div>
        </div>

        {/* Right Column (7 cols): Cash Burn Trajectory & Key Metric Readouts */}
        <div className="lg:col-span-7 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold text-white">Cash Burn Trajectory (12-Month Forecast)</h3>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 text-[10px] font-bold">
                  Cash Runway: {simulator.simulatedCashRunwayMonths} Months
                </span>
              </div>
            </div>
            <CashBurnChart trajectoryPoints={simulator.trajectoryPoints} />
          </div>

          {/* Bottom KPI metric blocks */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-800 text-center">
            <div className="p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
              <div className="text-[10px] text-slate-400">Simulated Runway</div>
              <div className="text-sm font-bold text-amber-400 font-mono mt-0.5">{simulator.simulatedCashRunwayMonths} Mo</div>
            </div>

            <div className="p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
              <div className="text-[10px] text-slate-400">Delta vs Baseline</div>
              <div className={`text-sm font-bold font-mono mt-0.5 ${simulator.deltaVsBaselineMonths >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {simulator.deltaVsBaselineMonths >= 0 ? `+${simulator.deltaVsBaselineMonths}` : simulator.deltaVsBaselineMonths} Mo
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
              <div className="text-[10px] text-slate-400">Projected Ending Cash</div>
              <div className="text-sm font-bold text-white font-mono mt-0.5">
                ${(simulator.projectedEndingCash / 1e6).toFixed(2)}M
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
              <div className="text-[10px] text-slate-400">Net Impact %</div>
              <div className={`text-sm font-bold font-mono mt-0.5 ${simulator.netImpactPct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {simulator.netImpactPct >= 0 ? `+${simulator.netImpactPct}%` : `${simulator.netImpactPct}%`}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
