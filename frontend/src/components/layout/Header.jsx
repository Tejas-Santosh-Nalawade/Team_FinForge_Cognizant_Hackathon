import React from 'react';
import {
  FileText,
  Download,
  CheckCircle2,
  AlertCircle,
  Database,
  TrendingUp,
  ShieldCheck,
  Flag,
  Share2,
  FileCheck,
  LogOut,
} from 'lucide-react';
import { useEngagementStore } from '../../stores/useEngagementStore';
import { buildReportDeliverables, openArtifact } from '../../api/client';

export const Header = () => {
  const { activeTab, setActiveTab, engagement, summary, session, endSession } = useEngagementStore();

  const handleExportPDF = async () => {
    try {
      const res = await buildReportDeliverables({ engagement_id: engagement.id });
      if (res && res.pdf_wp514_url) {
        openArtifact(res.pdf_wp514_url);
      } else {
        alert('The report service did not return a PDF link.');
      }
    } catch (e) {
      alert('PDF export could not be completed. Ingest an engagement first, then try again.');
    }
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(engagement, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Audit_Assurance_Payload_${engagement.periodEnding}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const steps = [
    { id: 'planning', num: '1', title: 'Planning', sub: 'Risk & Materiality', icon: ShieldCheck },
    { id: 'ingestion', num: '2', title: 'Data & Ingestion', sub: 'Collect & Validate', icon: Database },
    { id: 'analytics', num: '3', title: 'Analytics', sub: 'BvA & Ratios', icon: TrendingUp },
    { id: 'execution', num: '4', title: 'Audit Execution', sub: '56-Rule Suite', icon: CheckCircle2 },
    { id: 'findings', num: '5', title: 'Findings', sub: 'Root Cause & RAG', icon: Flag },
    { id: 'simulator', num: 'S', title: 'Simulator', sub: 'What-If Drivers', icon: TrendingUp },
    { id: 'reporting', num: '6', title: 'Reporting', sub: 'Working Papers', icon: FileText },
    { id: 'closure', num: '7', title: 'Closure', sub: 'Sign-off & Close', icon: FileCheck },
  ];

  return (
    <header className="bg-[#0B1120] border-b border-[#1E293B] px-6 py-3 select-none">
      {/* Top row: Brand + Status + Actions */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pb-3">
        {/* Entity details */}
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-sky-500/20 ring-1 ring-white/20">
            <span className="text-white font-black text-lg tracking-wider">A</span>
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-lg font-bold text-white tracking-tight">{engagement.clientName}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-950/80 text-sky-400 border border-sky-800/60 font-mono">
                {engagement.id}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              FP&A Audit Assurance Suite &nbsp;•&nbsp; <span className="text-slate-300 font-medium">{engagement.framework}</span> &nbsp;•&nbsp; Period Ending <span className="text-slate-300 font-mono">{engagement.periodEnding}</span>
            </p>
          </div>
        </div>

        {/* Middle: Pass Score Pill */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2.5 px-3 py-1.5 rounded-lg bg-red-950/40 border border-red-800/50">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-bold text-red-400 uppercase tracking-wide">
                  {engagement.riskStatus === 'CLEAN' ? 'AUDIT CLEARED' : 'REVIEW REQUIRED'}
                </span>
                <span className="text-xs text-slate-300 font-mono">
                  {summary.passedProcedures} / {summary.totalProcedures} Procedures Passed
                </span>
              </div>
              <div className="text-[10px] text-slate-400">
                <span className="text-emerald-400 font-bold">{summary.passScorePct}%</span> Overall Pass Score
              </div>
            </div>
          </div>
        </div>

        {/* Right Quick Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleExportPDF}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold shadow-md shadow-sky-600/30 transition active:scale-95 cursor-pointer"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Export WP-514 PDF</span>
          </button>
          <button
            onClick={handleExportJSON}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#581C87] hover:bg-[#6B21A8] text-purple-200 text-xs font-semibold shadow-md border border-purple-700/50 transition active:scale-95 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON Payload</span>
          </button>
          <button
            onClick={handleExportPDF}
            className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition active:scale-95 cursor-pointer"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Export All (ZIP)</span>
          </button>
          <button
            onClick={endSession}
            title={`Sign out ${session.user?.email || ''}`}
            className="flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-slate-300 transition hover:border-slate-500 hover:text-white"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span className="hidden xl:inline">Sign out</span>
          </button>
        </div>
      </div>

      {/* Bottom row: Stepper Workflow Pipeline */}
      <div className="pt-2 border-t border-slate-800/80 overflow-x-auto pb-1 scrollbar-none">
        <div className="flex items-center min-w-[760px] justify-between gap-2">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            const isActive = activeTab === s.id;
            return (
              <button
                key={s.id}
                onClick={() => setActiveTab(s.id)}
                className={`flex items-center space-x-2.5 px-3 py-1.5 rounded-lg transition text-left cursor-pointer border ${
                  isActive
                    ? 'bg-sky-950/70 border-sky-500/80 text-white shadow-sm shadow-sky-500/20'
                    : 'bg-[#0F172A]/80 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isActive ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {s.num}
                </div>
                <div className="leading-tight">
                  <div className={`text-xs font-semibold ${isActive ? 'text-sky-300' : 'text-slate-300'}`}>{s.title}</div>
                  <div className="text-[10px] text-slate-400">{s.sub}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
