import React, { useState } from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import { uploadStatementFile } from '../api/client';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Server,
  ShieldCheck,
  ArrowRight
} from 'lucide-react';

export const IngestionDashboard = () => {
  const { hydrateAuditRun, setActiveTab } = useEngagementStore();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('IDLE'); // IDLE | UPLOADING | SUCCESS | ERROR
  const [selectedFileName, setSelectedFileName] = useState('');
  const [uploadError, setUploadError] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFileName(file.name);
    setIsUploading(true);
    setUploadError('');
    setUploadProgress(25);
    setUploadStatus('UPLOADING');

    try {
      setUploadProgress(60);
      const res = await uploadStatementFile(file);
      setUploadProgress(100);
      setUploadStatus('SUCCESS');

      if (!res?.engagement_id) throw new Error('The audit service did not return an engagement ID.');
      hydrateAuditRun(res);
    } catch (e) {
      setUploadStatus('ERROR');
      setUploadProgress(0);
      setUploadError(e.response?.data?.detail || e.message || 'Upload could not be completed.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Ingestion Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Connected Data Sources</div>
          <div className="text-2xl font-bold text-white mt-1">12 <span className="text-xs text-slate-400 font-normal">Active Connectors</span></div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center">
            <CheckCircle2 className="w-3 h-3 mr-1" /> ERP, GL, Payroll, Footnotes
          </div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Total Tables Ingested</div>
          <div className="text-2xl font-bold text-white mt-1">48 <span className="text-xs text-slate-400 font-normal">Schedules</span></div>
          <div className="text-[11px] text-sky-400 mt-1">2.43M Extracted Records</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Data Quality Score</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">98.2% <span className="text-xs text-slate-400 font-normal">Overall</span></div>
          <div className="text-[11px] text-slate-400 mt-1">CoA Normalization 100%</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Cloud Storage Destination</div>
          <div className="text-sm font-bold text-white mt-1">Cloudflare R2 Bucket</div>
          <div className="text-[11px] text-purple-400 mt-1 font-mono">s3.r2.cloudflarestorage.com</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Drag & Drop Dropzone + Live Upload Checklist */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-6">
            <h2 className="text-sm font-bold text-white mb-2 flex items-center justify-between">
              <span>Financial Statements &amp; Footnote Ingestion Dropzone</span>
              <span className="text-[10px] text-slate-400 font-mono">Supported: .xlsx, .xls, .json</span>
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Upload multi-tab financial statement packages containing Balance Sheet, Income Statement, Cash Flow, AR Aging, PP&E Roll-forward, and Debt Maturity schedules.
            </p>

            {/* Dropzone container */}
            <label className="border-2 border-dashed border-sky-600/40 hover:border-sky-500 rounded-xl p-8 flex flex-col items-center justify-center bg-slate-900/50 hover:bg-slate-900/80 transition cursor-pointer group">
              <UploadCloud className="w-12 h-12 text-sky-400 group-hover:scale-110 transition mb-3" />
              <div className="text-sm font-semibold text-white">Drag &amp; drop financial workbook or click to browse</div>
              <div className="text-xs text-slate-400 mt-1">Auto-mapped to Canonical Chart of Accounts &amp; 56-Rule Audit Gate</div>
              <input
                type="file"
                className="hidden"
                accept=".xlsx,.xls,.json"
                onChange={handleFileUpload}
              />
            </label>

            {/* Upload progress feedback */}
            {isUploading && (
              <div className="mt-4 p-4 rounded-lg bg-[#0B1120] border border-slate-800 space-y-2">
                <div className="flex justify-between text-xs text-slate-300">
                  <span className="flex items-center space-x-2">
                    <RefreshCw className="w-3.5 h-3.5 text-sky-400 animate-spin" />
                    <span>Uploading {selectedFileName} to Cloudflare R2...</span>
                  </span>
                  <span className="font-mono text-sky-400 font-bold">{uploadProgress}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 rounded-full transition-all duration-300" style={{ width: `${uploadProgress}%` }}></div>
                </div>
              </div>
            )}

            {uploadStatus === 'SUCCESS' && (
              <div className="mt-4 p-4 rounded-lg bg-emerald-950/40 border border-emerald-800/60 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <div>
                    <div className="text-xs font-bold text-white">Ingestion &amp; 56-Rule Audit Gate Complete</div>
                    <div className="text-[11px] text-slate-400">All statements normalized and 56 deterministic procedures executed.</div>
                  </div>
                </div>
                <button
                  onClick={() => setActiveTab('execution')}
                  className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition"
                >
                  <span>Review Audit Gate</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {uploadStatus === 'ERROR' && (
              <div className="mt-4 p-4 rounded-lg bg-red-950/30 border border-red-800/60 text-xs text-red-200">
                <span className="font-bold">Upload not completed.</span> {uploadError}
              </div>
            )}
          </div>

          {/* Source Systems Table */}
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5">
            <h3 className="text-xs font-bold text-white mb-3 flex items-center space-x-2">
              <Server className="w-4 h-4 text-indigo-400" />
              <span>Connected Financial Source Systems</span>
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#0B1120] text-slate-400 uppercase text-[10px]">
                  <tr>
                    <th className="py-2 px-3">Source System</th>
                    <th className="py-2 px-3">Connection Status</th>
                    <th className="py-2 px-3">Last Ingested</th>
                    <th className="py-2 px-3">Records</th>
                    <th className="py-2 px-3">Integrity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300">
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">Oracle ERP Financials</td>
                    <td className="py-2.5 px-3"><span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 text-[10px] font-bold border border-emerald-800">Connected</span></td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">2025-06-02 11:30 AM</td>
                    <td className="py-2.5 px-3 font-mono">1.20M</td>
                    <td className="py-2.5 px-3 text-emerald-400">100%</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">General Ledger Trial Balance</td>
                    <td className="py-2.5 px-3"><span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 text-[10px] font-bold border border-emerald-800">Synced</span></td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">2025-06-02 11:32 AM</td>
                    <td className="py-2.5 px-3 font-mono">485K</td>
                    <td className="py-2.5 px-3 text-emerald-400">99.8%</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">Accounts Payable Subledger</td>
                    <td className="py-2.5 px-3"><span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 text-[10px] font-bold border border-emerald-800">Synced</span></td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">2025-06-02 11:33 AM</td>
                    <td className="py-2.5 px-3 font-mono">320K</td>
                    <td className="py-2.5 px-3 text-emerald-400">100%</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 px-3 font-semibold text-white">Bank Confirmation Feeds</td>
                    <td className="py-2.5 px-3"><span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 text-[10px] font-bold border border-emerald-800">Verified</span></td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">2025-06-02 11:35 AM</td>
                    <td className="py-2.5 px-3 font-mono">120K</td>
                    <td className="py-2.5 px-3 text-emerald-400">100%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Data Quality Checklist */}
        <div className="space-y-6">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5">
            <h3 className="text-xs font-bold text-white mb-4 flex items-center justify-between">
              <span>Data Quality &amp; Completeness</span>
              <span className="text-emerald-400 font-mono font-bold">98.2%</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
                <span className="text-slate-400">Completeness Check</span>
                <span className="font-mono font-bold text-emerald-400">99%</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
                <span className="text-slate-400">Consistency Audit</span>
                <span className="font-mono font-bold text-emerald-400">98%</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
                <span className="text-slate-400">Format Validation</span>
                <span className="font-mono font-bold text-emerald-400">100%</span>
              </div>
              <div className="flex justify-between items-center p-2.5 rounded-lg bg-[#0B1120] border border-slate-800">
                <span className="text-slate-400">Reconciliation Footings</span>
                <span className="font-mono font-bold text-amber-400">96%</span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800">
              <div className="text-xs font-bold text-white mb-2">Ingestion Checklist</div>
              <div className="space-y-2 text-[11px] text-slate-300">
                <div className="flex items-center space-x-2 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Balance Sheet Normalized</span>
                </div>
                <div className="flex items-center space-x-2 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Income Statement Normalized</span>
                </div>
                <div className="flex items-center space-x-2 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Cash Flow Statement Reconciled</span>
                </div>
                <div className="flex items-center space-x-2 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Footnotes &amp; Schedules Extracted</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
