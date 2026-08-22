import React, { useState } from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import {
  Flag,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  Sparkles,
  ShieldAlert,
  FileCheck,
  Send,
  HelpCircle,
} from 'lucide-react';
import { explainFindingWithRAG } from '../api/client';

export const FindingsDashboard = () => {
  const {
    findings,
    selectedFinding,
    setSelectedFinding,
    resolveFindingAction,
    riskBanner,
    engagement,
  } = useEngagementStore();

  const currentFinding = selectedFinding || findings[0] || {};
  const [justificationNotes, setJustificationNotes] = useState(currentFinding.notes || '');
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState(null);

  const handleSelectFinding = (finding) => {
    setSelectedFinding(finding);
    setJustificationNotes(finding.notes || '');
    setAiAnalysis(null);
  };

  const handleDecision = async (decision) => {
    if (!currentFinding.id) return;
    await resolveFindingAction(currentFinding.id, decision, justificationNotes);
  };

  const handleAskGeminiRAG = async () => {
    setIsAiLoading(true);
    try {
      const res = await explainFindingWithRAG({
        rule_id: currentFinding.rule_id || 'RATIO_02',
        category: currentFinding.category,
        description: currentFinding.title,
      });
      if (res && res.status === 'success') {
        setAiAnalysis(res);
      }
    } catch (e) {
      console.log('Using built-in RAG synthesis fallback');
      setAiAnalysis({
        root_cause: currentFinding.rootCause,
        asc_ifrs_reference: currentFinding.ascIfrsReference,
        recommended_resolution: currentFinding.recommendedResolution,
      });
    } finally {
      setIsAiLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Findings Detected</div>
          <div className="text-2xl font-bold text-white mt-1">3 <span className="text-xs text-slate-400 font-normal">Exceptions</span></div>
          <div className="text-[11px] text-sky-400 mt-1">Deterministic &amp; Ratio Triggers</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Open For Resolution</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {findings.filter((f) => f.resolutionDecision === 'UNRESOLVED').length} <span className="text-xs text-slate-400 font-normal">Pending</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1">Decision Matrix Active</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">High / Critical Severity</div>
          <div className="text-2xl font-bold text-red-400 mt-1">2 <span className="text-xs text-slate-400 font-normal">Critical</span></div>
          <div className="text-[11px] text-red-400 mt-1">Liquidity &amp; CECL Provisioning</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">RAG Standard Retrieval</div>
          <div className="text-sm font-bold text-white mt-1">Qdrant + Google Gemini</div>
          <div className="text-[11px] text-purple-400 mt-1">US GAAP ASC / IFRS Indexed</div>
        </div>
      </div>

      {/* Split Screen Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (4 cols): Findings List */}
        <div className="lg:col-span-4 space-y-3">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
            Audit Findings List
          </div>
          {findings.map((f) => {
            const isSelected = (currentFinding.id === f.id);
            return (
              <div
                key={f.id}
                onClick={() => handleSelectFinding(f)}
                className={`p-4 rounded-xl border transition cursor-pointer ${
                  isSelected
                    ? 'bg-[#1E293B]/90 border-sky-500 shadow-md shadow-sky-500/10'
                    : 'bg-[#0F172A] border-[#1E293B] hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="font-mono text-sky-400 font-bold">{f.id}</span>
                  <div className="flex items-center space-x-1.5">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        f.severity === 'Critical'
                          ? 'bg-red-950 text-red-400 border border-red-800'
                          : 'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}
                    >
                      {f.severity}
                    </span>
                    {f.resolutionDecision !== 'UNRESOLVED' && (
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          f.resolutionDecision === 'ACCEPTED'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : 'bg-red-950 text-red-400 border border-red-800'
                        }`}
                      >
                        {f.resolutionDecision}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-xs font-semibold text-white mb-1">{f.title}</div>
                <div className="text-[11px] text-slate-400 flex items-center justify-between">
                  <span>{f.category}</span>
                  <span className="font-mono text-slate-300">{f.workingPaper}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column (8 cols): Finding Detail & Root Cause Explorer */}
        <div className="lg:col-span-8 bg-[#0F172A] border border-[#1E293B] rounded-xl p-6 space-y-6">
          {/* Header row */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-4 border-b border-slate-800">
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs text-sky-400 font-bold">{currentFinding.id}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-400 border border-red-800">
                  {currentFinding.severity}
                </span>
                <span className="text-xs text-slate-400 font-mono">Rule: {currentFinding.rule_id}</span>
              </div>
              <h2 className="text-base font-bold text-white mt-1">{currentFinding.title}</h2>
            </div>

            <button
              onClick={handleAskGeminiRAG}
              disabled={isAiLoading}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md transition active:scale-95 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isAiLoading ? 'Synthesizing with Gemini...' : 'Ask AI & RAG Advisor'}</span>
            </button>
          </div>

          {/* Variance Analysis Box */}
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Variance Analysis</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-lg bg-[#0B1120] border border-slate-800">
                <div className="text-[10px] text-slate-500">Metric</div>
                <div className="text-xs font-bold text-white mt-0.5">{currentFinding.category}</div>
              </div>
              <div className="p-3 rounded-lg bg-[#0B1120] border border-slate-800">
                <div className="text-[10px] text-slate-500">Expected (Threshold)</div>
                <div className="text-xs font-bold text-emerald-400 font-mono mt-0.5">{currentFinding.expected}</div>
              </div>
              <div className="p-3 rounded-lg bg-[#0B1120] border border-slate-800">
                <div className="text-[10px] text-slate-500">Actual (Reported)</div>
                <div className="text-xs font-bold text-amber-400 font-mono mt-0.5">{currentFinding.actual}</div>
              </div>
              <div className="p-3 rounded-lg bg-[#0B1120] border border-slate-800">
                <div className="text-[10px] text-slate-500">Variance %</div>
                <div className="text-xs font-bold text-red-400 font-mono mt-0.5">{currentFinding.variance}</div>
              </div>
            </div>
          </div>

          {/* Root Cause Section */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-slate-300 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <span>Root Cause Analysis</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {aiAnalysis?.root_cause || currentFinding.rootCause}
            </p>
          </div>

          {/* ASC / IFRS Authoritative Standard Box (Qdrant Vector Retrieval) */}
          <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-800/40 space-y-2">
            <div className="text-xs font-bold text-sky-400 flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-sky-400" />
              <span>Authoritative Regulatory Standard (US GAAP / IFRS Policy)</span>
            </div>
            <p className="text-xs text-slate-300 font-mono whitespace-pre-line leading-relaxed">
              {aiAnalysis?.asc_ifrs_reference || currentFinding.ascIfrsReference}
            </p>
          </div>

          {/* Recommended Resolution */}
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/40 space-y-2">
            <div className="text-xs font-bold text-emerald-400 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Recommended Resolution &amp; Remediation Plan</span>
            </div>
            <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed">
              {aiAnalysis?.recommended_resolution || currentFinding.recommendedResolution}
            </p>
          </div>

          {/* Decision Matrix & Waiver Action Controls */}
          <div className="pt-4 border-t border-slate-800 space-y-4">
            <h3 className="text-xs font-bold text-white flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Auditor Decision &amp; Adjusting Journal Entry (AJE) Control</span>
            </h3>

            <div>
              <label className="block text-[11px] text-slate-400 mb-1">
                Auditor Justification / Reconciling Notes (Required for Waivers):
              </label>
              <textarea
                rows={2}
                value={justificationNotes}
                onChange={(e) => setJustificationNotes(e.target.value)}
                placeholder="Enter audit rationale or GL journal entry reference..."
                className="w-full bg-[#0B1120] border border-slate-800 rounded-lg p-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="text-[11px] text-slate-400">
                Current Status:{' '}
                <span className="font-bold text-white font-mono">
                  {currentFinding.resolutionDecision || 'UNRESOLVED'}
                </span>
              </div>

              <div className="flex items-center space-x-3 w-full sm:w-auto">
                <button
                  onClick={() => handleDecision('ACCEPTED')}
                  className="flex-1 sm:flex-none px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-600/20 transition active:scale-95 cursor-pointer flex items-center justify-center space-x-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Accept Correction (Apply AJE)</span>
                </button>

                <button
                  onClick={() => handleDecision('WAIVED')}
                  className="flex-1 sm:flex-none px-4 py-2 rounded-lg bg-red-800 hover:bg-red-700 text-white text-xs font-bold shadow-md shadow-red-800/20 transition active:scale-95 cursor-pointer flex items-center justify-center space-x-1.5"
                >
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Waive / Reject (Keep Original)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
