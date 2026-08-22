import React, { useState } from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import { StatusBadge } from '../components/ui/KPICard';
import {
  FileCheck,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';

export const AuditExecutionDashboard = () => {
  const { procedures, summary, setActiveTab, setSelectedFinding, findings } = useEngagementStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');

  const filteredProcedures = procedures.filter((p) => {
    const matchesSearch =
      p.procedure.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'ALL' || p.category === selectedCategory;
    const matchesSeverity = selectedSeverity === 'ALL' || p.severity === selectedSeverity;
    const matchesStatus = selectedStatus === 'ALL' || p.status === selectedStatus;
    return matchesSearch && matchesCategory && matchesSeverity && matchesStatus;
  });

  const handleRowClick = (proc) => {
    if (proc.status === 'FLAGGED' || proc.status === 'FAIL') {
      const match = findings.find((f) => f.rule_id === proc.reference) || findings[0];
      setSelectedFinding(match);
      setActiveTab('findings');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top summary counter cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400">Total Audit Rules</div>
            <div className="text-2xl font-bold text-white mt-1">{summary.totalProcedures}</div>
            <div className="text-[11px] text-sky-400 mt-0.5">Deterministic 56-Rule Suite</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 font-bold">
            56
          </div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400">Passed Verification</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.passedProcedures}</div>
            <div className="text-[11px] text-emerald-400 mt-0.5">{summary.passScorePct}% Clean Tie-Outs</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400">Flagged / Exceptions</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.flaggedProcedures}</div>
            <div className="text-[11px] text-amber-400 mt-0.5">Discrepancy Resolution Needed</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400">Resolution Decision</div>
            <div className="text-sm font-bold text-white mt-1">Accept vs Waive</div>
            <button
              onClick={() => setActiveTab('findings')}
              className="text-[11px] text-sky-400 hover:underline flex items-center mt-1"
            >
              Open Resolution Console <ArrowRight className="w-3 h-3 ml-1" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Console Section */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <FileCheck className="w-4 h-4 text-cyan-400" />
              <span>Audit Verification &amp; Flag Console (56-Rule Suite)</span>
            </h2>
            <p className="text-[11px] text-slate-400">Mathematical Footing Rules, Cross-Statement Tie-Outs, and Guardrail Assertions</p>
          </div>

          {/* Filters & Search */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search rules, references..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-[#0B1120] border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 w-48"
              />
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
            >
              <option value="ALL">All Categories</option>
              <option value="Internal Consistency">Internal Consistency</option>
              <option value="Liquidity Ratios">Liquidity Ratios</option>
              <option value="Profitability Ratios">Profitability Ratios</option>
              <option value="Cross-Statement Tie-Out">Cross-Statement Tie-Out</option>
              <option value="Disclosure & Footnotes">Disclosure &amp; Footnotes</option>
            </select>

            {/* Severity Filter */}
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
            >
              <option value="ALL">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>

            {/* Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-sky-500"
            >
              <option value="ALL">All Status</option>
              <option value="PASS">PASS</option>
              <option value="FLAGGED">FLAGGED</option>
              <option value="FAIL">FAIL</option>
            </select>
          </div>
        </div>

        {/* Procedures Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#0B1120] text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Rule #</th>
                <th className="py-2.5 px-3">Reference</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Procedure Description</th>
                <th className="py-2.5 px-3 text-center">Severity</th>
                <th className="py-2.5 px-3 text-center">Status</th>
                <th className="py-2.5 px-3 text-center">Evidence</th>
                <th className="py-2.5 px-3">Last Run</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredProcedures.map((proc, idx) => (
                <tr
                  key={idx}
                  onClick={() => handleRowClick(proc)}
                  className={`hover:bg-slate-800/40 transition cursor-pointer ${
                    proc.status === 'FLAGGED' ? 'bg-amber-950/10' : ''
                  }`}
                >
                  <td className="py-2.5 px-3 font-mono text-slate-400">{String(proc.step).padStart(2, '0')}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-sky-400">{proc.reference}</td>
                  <td className="py-2.5 px-3 text-slate-300">{proc.category}</td>
                  <td className="py-2.5 px-3 font-medium text-white max-w-xs truncate">{proc.procedure}</td>
                  <td className="py-2.5 px-3 text-center">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        proc.severity === 'Critical'
                          ? 'bg-red-950 text-red-400 border border-red-800'
                          : proc.severity === 'High'
                          ? 'bg-amber-950 text-amber-400 border border-amber-800'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {proc.severity}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <StatusBadge status={proc.status} />
                  </td>
                  <td className="py-2.5 px-3 text-center font-mono text-[11px] text-sky-400 hover:underline">
                    {proc.evidence}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400">{proc.lastRun}</td>
                  <td className="py-2.5 px-3 text-right">
                    {proc.status === 'FLAGGED' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRowClick(proc);
                        }}
                        className="px-2.5 py-1 rounded bg-amber-600 hover:bg-amber-500 text-black font-bold text-[10px] transition shadow"
                      >
                        Resolve
                      </button>
                    ) : (
                      <span className="text-[11px] text-slate-500">Verified</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>Showing 1 to {filteredProcedures.length} of 56 entries</div>
          <div className="flex items-center space-x-1">
            <button className="px-2 py-1 rounded bg-[#0B1120] border border-slate-800 text-slate-400 hover:text-white">1</button>
            <button className="px-2 py-1 rounded bg-[#0B1120] border border-slate-800 text-slate-400 hover:text-white">2</button>
            <button className="px-2 py-1 rounded bg-[#0B1120] border border-slate-800 text-slate-400 hover:text-white">3</button>
          </div>
        </div>
      </div>
    </div>
  );
};
