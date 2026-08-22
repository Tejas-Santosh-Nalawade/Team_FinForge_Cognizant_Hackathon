import React, { useState } from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import { CheckCircle2, UserCheck, ShieldCheck, Clock, CheckSquare, Award } from 'lucide-react';

export const ClosureDashboard = () => {
  const { engagement, summary } = useEngagementStore();
  const [analystSigned, setAnalystSigned] = useState(true);
  const [managerSigned, setManagerSigned] = useState(false);
  const [partnerSigned, setPartnerSigned] = useState(false);
  const [closureCompleted, setClosureCompleted] = useState(false);

  const handleManagerApprove = () => {
    setManagerSigned(true);
  };

  const handlePartnerApprove = () => {
    setPartnerSigned(true);
    setClosureCompleted(true);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Overview */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-sky-400 text-xs font-bold uppercase tracking-wider mb-1">
            <CheckSquare className="w-4 h-4" />
            <span>Audit Assurance Sign-off &amp; Engagement Closure</span>
          </div>
          <h2 className="text-xl font-bold text-white">Hierarchical Audit Sign-Off Workflow</h2>
          <p className="text-xs text-slate-400 mt-1">
            Multi-tier verification adhering to PCAOB, AICPA, and US GAAP / IFRS engagement standards.
          </p>
        </div>

        {closureCompleted ? (
          <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-emerald-950/80 border border-emerald-500/60 text-emerald-300">
            <Award className="w-5 h-5 text-emerald-400" />
            <span className="text-xs font-bold">Audit Completed Successfully!</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-sky-950/80 border border-sky-500/60 text-sky-300">
            <Clock className="w-4 h-4 text-sky-400 animate-pulse" />
            <span className="text-xs font-bold">Manager / Partner Review In Progress</span>
          </div>
        )}
      </div>

      {/* 4-Tier Sign-Off Steps */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Tier 1: Analyst */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">1. Audit Analyst</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
              Completed
            </span>
          </div>
          <div className="flex items-center space-x-3 pt-2">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-white font-bold text-sm">
              AA
            </div>
            <div>
              <div className="text-xs font-bold text-white">Lead Assurance Senior</div>
              <div className="text-[11px] text-slate-400">Verified 56 Math Rules</div>
            </div>
          </div>
          <div className="text-[11px] text-emerald-400 flex items-center pt-2 border-t border-slate-800">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Digitally Signed (2026-08-18)
          </div>
        </div>

        {/* Tier 2: Manager */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">2. Audit Manager</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${managerSigned ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}`}>
              {managerSigned ? 'Approved' : 'In Review'}
            </span>
          </div>
          <div className="flex items-center space-x-3 pt-2">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-white font-bold text-sm">
              AM
            </div>
            <div>
              <div className="text-xs font-bold text-white">Engagement Manager</div>
              <div className="text-[11px] text-slate-400">Reviews Flagged Items &amp; AJEs</div>
            </div>
          </div>
          <div className="pt-2 border-t border-slate-800">
            {!managerSigned ? (
              <button
                onClick={handleManagerApprove}
                className="w-full py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold transition shadow cursor-pointer"
              >
                Approve &amp; Forward
              </button>
            ) : (
              <div className="text-[11px] text-emerald-400 flex items-center">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Approved by Manager
              </div>
            )}
          </div>
        </div>

        {/* Tier 3: Partner */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">3. Audit Partner</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${partnerSigned ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
              {partnerSigned ? 'Concurred' : 'Pending'}
            </span>
          </div>
          <div className="flex items-center space-x-3 pt-2">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-white font-bold text-sm">
              AP
            </div>
            <div>
              <div className="text-xs font-bold text-white">Partner-in-Charge</div>
              <div className="text-[11px] text-slate-400">Final Risk Assessment &amp; Opinion</div>
            </div>
          </div>
          <div className="pt-2 border-t border-slate-800">
            {managerSigned && !partnerSigned ? (
              <button
                onClick={handlePartnerApprove}
                className="w-full py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow cursor-pointer"
              >
                Sign Final Audit Report
              </button>
            ) : partnerSigned ? (
              <div className="text-[11px] text-emerald-400 flex items-center">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Partner Concurred
              </div>
            ) : (
              <div className="text-[11px] text-slate-500">Awaiting Manager Sign-off</div>
            )}
          </div>
        </div>

        {/* Tier 4: Client & Closure */}
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">4. Client Closure</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${closureCompleted ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
              {closureCompleted ? 'Archived' : 'Pending'}
            </span>
          </div>
          <div className="flex items-center space-x-3 pt-2">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-white font-bold text-sm">
              CL
            </div>
            <div>
              <div className="text-xs font-bold text-white">Apex Global Management</div>
              <div className="text-[11px] text-slate-400">Receives Final WP-514 &amp; Model</div>
            </div>
          </div>
          <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
            {closureCompleted ? 'Vault Sealed & Archived in R2' : 'Pending partner closure'}
          </div>
        </div>
      </div>

      {/* Closure Metrics Summary */}
      <div className="p-6 rounded-xl bg-[#0B1120] border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">Engagement Closed &amp; Archived as per Audit Policy</div>
            <div className="text-xs text-slate-400 mt-0.5">
              56 / 56 Procedures Documented &nbsp;•&nbsp; 2 Discrepancies Logged &nbsp;•&nbsp; Final Report Issued
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-400 font-mono">Archive Reference: VAULT-2025-WP514</span>
        </div>
      </div>
    </div>
  );
};
