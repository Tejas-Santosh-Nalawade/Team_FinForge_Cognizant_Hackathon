import React, { useState } from 'react';
import { useEngagementStore } from '../stores/useEngagementStore';
import { buildReportDeliverables, openArtifact } from '../api/client';
import {
  FileText,
  Download,
  Share2,
  CheckCircle2,
  FileSpreadsheet,
  Code2,
  Sliders,
  Settings,
  ShieldAlert,
} from 'lucide-react';

export const ReportingDashboard = () => {
  const { engagement, summary, riskBanner } = useEngagementStore();
  const [isBuilding, setIsBuilding] = useState(false);
  const [downloadUrls, setDownloadUrls] = useState(null);
  const [deliveryError, setDeliveryError] = useState('');

  const handleGenerateDeliverables = async (artifactType) => {
    setIsBuilding(true);
    setDeliveryError('');
    try {
      const res = await buildReportDeliverables({
        engagement_id: engagement.id,
      });
      if (res && res.status === 'success') {
        setDownloadUrls(res);
        if (artifactType) openArtifact(res[artifactType]);
      } else {
        throw new Error('The report service did not return downloadable artifacts.');
      }
    } catch (e) {
      setDeliveryError(e.response?.data?.detail || e.message || 'Deliverables could not be built.');
    } finally {
      setIsBuilding(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Deliverables Status</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">100% Ready</div>
          <div className="text-[11px] text-slate-400 mt-1">56 / 56 Working Papers Compiled</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Working Paper Set (PDF)</div>
          <div className="text-sm font-bold text-white mt-1">WP-514 Multi-Page Dossier</div>
          <div className="text-[11px] text-sky-400 mt-1">NumberedCanvas Two-Pass Render</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Reconciled Financial Model</div>
          <div className="text-sm font-bold text-white mt-1">Adjusted Trial Balance (.xlsx)</div>
          <div className="text-[11px] text-emerald-400 mt-1">openpyxl Audit Schedule</div>
        </div>

        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-4">
          <div className="text-xs text-slate-400">Audit Trail Payload</div>
          <div className="text-sm font-bold text-white mt-1">Structured JSON Payload</div>
          <div className="text-[11px] text-purple-400 mt-1">GAAP Citations &amp; Waiver Logs</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (8 cols): Working Paper Deliverables Viewer */}
        <div className="lg:col-span-8 bg-[#0F172A] border border-[#1E293B] rounded-xl p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                <FileText className="w-4 h-4 text-sky-400" />
                <span>WP-514 Working Paper Set &amp; Publication Hub</span>
              </h2>
              <p className="text-xs text-slate-400">Publication-grade audit documentation for regulatory and executive review.</p>
            </div>

            <button
              onClick={handleGenerateDeliverables}
              disabled={isBuilding}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold shadow-md shadow-sky-600/30 transition active:scale-95 cursor-pointer self-start sm:self-auto"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{isBuilding ? 'Compiling Artifacts...' : 'Build Deliverables'}</span>
            </button>
          </div>

          {/* Document Preview Card */}
          <div className="p-5 rounded-xl bg-[#0B1120] border border-slate-800 flex flex-col md:flex-row items-center gap-6">
            <div className="w-36 h-48 rounded-lg bg-white p-3 shadow-2xl flex flex-col justify-between shrink-0 text-slate-800 select-none">
              <div className="space-y-1.5">
                <div className="text-[7px] font-bold uppercase text-slate-900 border-b border-slate-300 pb-0.5">
                  Apex Global Technologies Inc.
                </div>
                <div className="text-[6px] text-slate-600">WP-514 Audit Assurance Set</div>
                <div className="w-full h-1 bg-slate-300 rounded"></div>
                <div className="w-3/4 h-1 bg-slate-200 rounded"></div>
                <div className="w-full h-1 bg-slate-200 rounded"></div>
                <div className="w-5/6 h-1 bg-slate-200 rounded"></div>
              </div>
              <div className="text-[5px] text-slate-400 flex justify-between border-t border-slate-200 pt-0.5">
                <span>Page 1 of 66</span>
                <span>WP-514</span>
              </div>
            </div>

            <div className="space-y-3 flex-1">
              <div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                  Ready for Sign-off
                </span>
                <h3 className="text-base font-bold text-white mt-1">WP-514 Working Paper Set (PDF)</h3>
                <div className="text-xs text-slate-400 mt-0.5">
                  Client: <span className="text-slate-200">{engagement.clientName}</span> &nbsp;|&nbsp; Period:{' '}
                  <span className="text-slate-200">{engagement.periodEnding}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Executive MD&amp;A Summary</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>56-Rule Audit Matrix</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Ratio Benchmarks</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Waiver &amp; AJE Ledger</span>
                </div>
              </div>

              {/* Download Buttons */}
              <div className="flex flex-wrap items-center gap-2 pt-2">
                <button
                  onClick={() => handleGenerateDeliverables('pdf_wp514_url')}
                  className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </button>
                <button
                  onClick={() => handleGenerateDeliverables('corrected_xlsx_url')}
                  className="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-semibold flex items-center space-x-1.5 transition cursor-pointer"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                  <span>Download Corrected Excel</span>
                </button>
                <button
                  onClick={() => handleGenerateDeliverables('json_payload_url')}
                  className="px-3 py-1.5 rounded-lg bg-purple-700 hover:bg-purple-600 text-white text-xs font-semibold flex items-center space-x-1.5 transition cursor-pointer"
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Download JSON</span>
                </button>
              </div>
            </div>
          </div>

          {deliveryError && (
            <div className="rounded-lg border border-red-800/60 bg-red-950/30 px-3 py-2 text-xs text-red-200">
              <span className="font-bold">Deliverables not built.</span> {deliveryError}
            </div>
          )}
        </div>

        {/* Right Column (4 cols): System Settings & Audit Parameters */}
        <div className="lg:col-span-4 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 space-y-4">
          <h3 className="text-xs font-bold text-white flex items-center space-x-2">
            <Settings className="w-4 h-4 text-slate-400" />
            <span>System Settings &amp; Configuration</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Audit Framework</label>
              <input
                type="text"
                readOnly
                value={engagement.framework}
                className="w-full bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Review Stage</label>
              <input
                type="text"
                readOnly
                value={engagement.reviewStage}
                className="w-full bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Materiality %</label>
                <input
                  type="text"
                  readOnly
                  value="2.0%"
                  className="w-full bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Performance %</label>
                <input
                  type="text"
                  readOnly
                  value="75%"
                  className="w-full bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Liquidity Threshold (Months)</label>
              <input
                type="text"
                readOnly
                value="12 Months"
                className="w-full bg-[#0B1120] border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
              />
            </div>

            <div className="pt-2 border-t border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Auto-flag Material Variances</span>
                <span className="w-8 h-4 bg-sky-600 rounded-full inline-block relative cursor-pointer">
                  <span className="w-3 h-3 bg-white rounded-full absolute right-0.5 top-0.5"></span>
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Real-time Anomaly Monitoring</span>
                <span className="w-8 h-4 bg-sky-600 rounded-full inline-block relative cursor-pointer">
                  <span className="w-3 h-3 bg-white rounded-full absolute right-0.5 top-0.5"></span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
