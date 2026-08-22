import React, { useState } from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import { KPICard } from '../components/ui/KPICard';
import { LiquidityTrendChart } from '../components/charts/LiquidityTrendChart';
import { TrendingUp, AlertCircle, ArrowUpRight, ArrowDownRight, Layers } from 'lucide-react';

export const AnalyticalDashboard = () => {
  const { summary } = useEngagementStore();
  const [statementTab, setStatementTab] = useState('is'); // is | bs | cf

  const incomeStatementRows = [
    { name: 'Revenue', cy: 22000000.0, py: 18000000.0, varDollar: 4000000.0, varPct: 22.2, threshold: '±10%', isFlagged: true },
    { name: 'Cost of Goods Sold (COGS)', cy: 10500000.0, py: 8600000.0, varDollar: 1900000.0, varPct: 22.1, threshold: '±10%', isFlagged: true },
    { name: 'Gross Profit', cy: 11500000.0, py: 9400000.0, varDollar: 2100000.0, varPct: 22.3, threshold: '±10%', isFlagged: true },
    { name: 'Operating Income', cy: 3040000.0, py: 2400000.0, varDollar: 640000.0, varPct: 26.7, threshold: '±10%', isFlagged: true },
    { name: 'Net Income', cy: 2760000.0, py: 1900000.0, varDollar: 860000.0, varPct: 45.3, threshold: '±10%', isFlagged: true },
    { name: 'Cash & Equivalents', cy: 12450000.0, py: 8500000.0, varDollar: 3950000.0, varPct: 46.5, threshold: '±15%', isFlagged: true },
    { name: 'Total Assets', cy: 24800000.0, py: 20300000.0, varDollar: 4500000.0, varPct: 22.2, threshold: '±15%', isFlagged: true },
    { name: 'Total Liabilities', cy: 8700000.0, py: 7200000.0, varDollar: 1500000.0, varPct: 20.8, threshold: '±15%', isFlagged: true },
    { name: 'Debt Maturity (12 Mo.)', cy: 3200000.0, py: 2100000.0, varDollar: 1100000.0, varPct: 52.4, threshold: '±15%', isFlagged: true },
  ];

  const balanceSheetRows = [
    { name: 'Cash & Cash Equivalents', cy: 12450000.0, py: 8500000.0, varDollar: 3950000.0, varPct: 46.5, threshold: '±15%', isFlagged: true },
    { name: 'Accounts Receivable, net', cy: 3920000.0, py: 3500000.0, varDollar: 420000.0, varPct: 12.0, threshold: '±10%', isFlagged: true },
    { name: 'Inventory', cy: 1400000.0, py: 1200000.0, varDollar: 200000.0, varPct: 16.7, threshold: '±10%', isFlagged: true },
    { name: 'Total Current Assets', cy: 18100000.0, py: 13300000.0, varDollar: 4800000.0, varPct: 36.1, threshold: '±15%', isFlagged: true },
    { name: 'PP&E, net', cy: 7800000.0, py: 6000000.0, varDollar: 1800000.0, varPct: 30.0, threshold: '±15%', isFlagged: true },
    { name: 'Total Assets', cy: 27100000.0, py: 20500000.0, varDollar: 6600000.0, varPct: 32.2, threshold: '±15%', isFlagged: true },
    { name: 'Accounts Payable', cy: 1880000.0, py: 1500000.0, varDollar: 380000.0, varPct: 25.3, threshold: '±10%', isFlagged: true },
    { name: 'Total Current Liabilities', cy: 3150000.0, py: 2300000.0, varDollar: 850000.0, varPct: 37.0, threshold: '±15%', isFlagged: true },
    { name: 'Total Liabilities', cy: 7800000.0, py: 5910000.0, varDollar: 1890000.0, varPct: 32.0, threshold: '±15%', isFlagged: true },
    { name: 'Total Equity', cy: 19300000.0, py: 14590000.0, varDollar: 4710000.0, varPct: 32.3, threshold: '±15%', isFlagged: true },
  ];

  const cashFlowRows = [
    { name: 'Net Income Starting', cy: 2760000.0, py: 1900000.0, varDollar: 860000.0, varPct: 45.3, threshold: '±10%', isFlagged: true },
    { name: 'Operating Cash Flow', cy: 3950000.0, py: 2800000.0, varDollar: 1150000.0, varPct: 41.1, threshold: '±15%', isFlagged: true },
    { name: 'Capital Expenditures (CapEx)', cy: -1200000.0, py: -850000.0, varDollar: -350000.0, varPct: 41.2, threshold: '±15%', isFlagged: true },
    { name: 'Investing Cash Flow', cy: -1200000.0, py: -850000.0, varDollar: -350000.0, varPct: 41.2, threshold: '±15%', isFlagged: true },
    { name: 'Financing Cash Flow', cy: 1200000.0, py: -500000.0, varDollar: 1700000.0, varPct: -340.0, threshold: '±15%', isFlagged: true },
    { name: 'Ending Cash Balance', cy: 12450000.0, py: 8500000.0, varDollar: 3950000.0, varPct: 46.5, threshold: '±15%', isFlagged: true },
  ];

  const activeRows = statementTab === 'is' ? incomeStatementRows : statementTab === 'bs' ? balanceSheetRows : cashFlowRows;

  return (
    <div className="space-y-6">
      {/* Top row: KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard
          title="Cash Runway"
          value={`${summary.cashRunwayMonths} Mo`}
          status="CRITICAL"
          statusText="CRITICAL"
          benchmark="< 12 Months"
          subValue="Monthly Burn $1.48M"
        />
        <KPICard
          title="Quick Ratio"
          value={`${summary.quickRatio}x`}
          status="CAUTION"
          statusText="CAUTION"
          benchmark="< 1.00x"
          subValue="Quick Assets / Cur. Liab"
        />
        <KPICard
          title="Current Ratio"
          value={`${summary.currentRatio}x`}
          status="HEALTHY"
          statusText="HEALTHY"
          benchmark="> 1.50x"
          subValue="Cur. Assets / Cur. Liab"
        />
        <KPICard
          title="Operating Margin"
          value={`${summary.operatingMarginPct}%`}
          status="CAUTION"
          statusText="BELOW BENCHMARK"
          benchmark="Target > 15.0%"
          subValue="EBIT / Total Revenue"
        />
        <KPICard
          title="56-Rule Suite Pass Score"
          value={`${summary.passScorePct}%`}
          status="HEALTHY"
          statusText="EXCELLENT"
          benchmark="Target > 95%"
          subValue="54 / 56 Clean Assertions"
        />
      </div>

      {/* Main Grid: BvA Variance Heatmap Table + Liquidity Trend Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: BvA Table with tab switcher */}
        <div className="lg:col-span-2 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                <span>Analytical Dashboard — BvA &amp; Variance Heatmap</span>
              </h2>
              <p className="text-[11px] text-slate-400">Horizontal YoY dollar &amp; percentage variance against materiality threshold</p>
            </div>

            {/* Statement Tabs */}
            <div className="flex items-center space-x-1 bg-[#0B1120] p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => setStatementTab('is')}
                className={`px-3 py-1 rounded text-xs font-semibold transition cursor-pointer ${
                  statementTab === 'is' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Income Statement
              </button>
              <button
                onClick={() => setStatementTab('bs')}
                className={`px-3 py-1 rounded text-xs font-semibold transition cursor-pointer ${
                  statementTab === 'bs' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Balance Sheet
              </button>
              <button
                onClick={() => setStatementTab('cf')}
                className={`px-3 py-1 rounded text-xs font-semibold transition cursor-pointer ${
                  statementTab === 'cf' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Cash Flow
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#0B1120] text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Line Item</th>
                  <th className="py-2.5 px-3">CY Actual (2025)</th>
                  <th className="py-2.5 px-3">PY Actual (2024)</th>
                  <th className="py-2.5 px-3">Variance ($)</th>
                  <th className="py-2.5 px-3">Variance (%)</th>
                  <th className="py-2.5 px-3">Threshold</th>
                  <th className="py-2.5 px-3 text-center">Flag</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {activeRows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-semibold text-white">{row.name}</td>
                    <td className="py-2.5 px-3 font-mono text-slate-200">
                      ${(row.cy / 1e6).toFixed(2)}M
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">
                      ${(row.py / 1e6).toFixed(2)}M
                    </td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400 font-medium">
                      +${(row.varDollar / 1e6).toFixed(2)}M
                    </td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400 font-bold">
                      +{row.varPct.toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">{row.threshold}</td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block shadow-sm shadow-red-500/50" title="Material Variance Flag"></span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span>Within Threshold</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                <span>Outside Threshold (Flagged)</span>
              </span>
            </div>
            <span>FLAG_01: Active Materiality Filter</span>
          </div>
        </div>

        {/* Right 1 Col: Liquidity Trend (12-Months) */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-white mb-1 flex items-center justify-between">
              <span>Liquidity Trend (12-Months)</span>
              <span className="text-[10px] text-amber-400 font-mono font-bold">8.4 Mo Runway</span>
            </h3>
            <p className="text-[11px] text-slate-400 mb-3">Actual Cash vs Baseline Burn Horizon</p>
            <LiquidityTrendChart />
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between items-center text-slate-400">
              <span>Ending Cash Position</span>
              <span className="font-mono font-bold text-white">$12.45M</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>Monthly Net Outflow</span>
              <span className="font-mono font-bold text-red-400">-$1.48M</span>
            </div>
            <div className="flex justify-between items-center text-slate-400">
              <span>Covenant Cushion</span>
              <span className="font-mono font-bold text-emerald-400">+$2.80M</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
