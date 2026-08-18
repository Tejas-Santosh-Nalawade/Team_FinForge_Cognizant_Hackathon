import React from 'react';
import { Activity, ArrowUpRight, ChevronRight, Database, FileCheck2, FileText, Flag, ShieldCheck, Sparkles, TrendingUp } from 'lucide-react';
import { useEngagementStore } from '../stores/useEngagementStore';

const defaultOverviewCards = [
  { key: 'planning', label: 'Planning', accent: 'text-sky-400', Icon: ShieldCheck, title: 'Planning Overview', value: '74% Done', meta: 'Materiality', detail: '$440K', cta: 'Review Inputs' },
  { key: 'ingestion', label: 'Ingestion', accent: 'text-indigo-400', Icon: Database, title: 'Source Lineage', value: '48 Tables', meta: 'Quality', detail: '98.2%', cta: 'View Lineage' },
  { key: 'analytics', label: 'Analytics', accent: 'text-emerald-400', Icon: TrendingUp, title: 'Liquidity', value: '8.4 Mo', meta: 'Quick ratio', detail: '0.88x', cta: 'Open Dashboard' },
  { key: 'execution', label: 'Audit Suite', accent: 'text-cyan-400', Icon: FileCheck2, title: 'Procedures', value: '56 Rules', meta: 'Pass Rate', detail: '96.4%', cta: 'Verify Controls' },
  { key: 'findings', label: 'Findings', accent: 'text-red-400', Icon: Flag, title: 'Open Exceptions', value: '3 Open', meta: 'Critical', detail: '1', cta: 'Resolve Risks' },
  { key: 'reporting', label: 'Reporting', accent: 'text-violet-400', Icon: FileText, title: 'Deliverables', value: '100% Ready', meta: 'Final Sign-off', detail: 'Ready', cta: 'Generate Pack' },
];

const defaultIngestionRows = [
  ['AR Ageing', '94%', 'Complete'],
  ['GL Mapping', '98%', 'Healthy'],
  ['Debt Schedule', '90%', 'Review'],
  ['PP&E Rollforward', '96%', 'Healthy'],
  ['Footnotes', '88%', 'Watch'],
];

const defaultAuditRows = [
  ['Cash & Equivalents', '98%', 'PASS'],
  ['Revenue Recognition', '94%', 'PASS'],
  ['Debt Covenant', '88%', 'FLAGGED'],
  ['Allowance', '92%', 'PASS'],
  ['Operating Lease', '90%', 'WATCH'],
];

const defaultFindings = [
  { name: 'ASC 606 - Revenue recognition', severity: 'High', owner: 'Audit Manager', status: 'Open' },
  { name: 'CECL allowance methodology', severity: 'Critical', owner: 'Controller', status: 'Review' },
  { name: 'Debt covenant sensitivity', severity: 'Medium', owner: 'Treasury', status: 'Open' },
];

export const PlanningDashboard = () => {
  const { engagement, summary, dashboard, setActiveTab } = useEngagementStore();
  const overviewCards = dashboard?.overviewCards?.length ? dashboard.overviewCards.map((card) => ({ ...card, Icon: { planning: ShieldCheck, ingestion: Database, analytics: TrendingUp, execution: FileCheck2, findings: Flag, reporting: FileText }[card.key] || ShieldCheck })) : defaultOverviewCards;
  const ingestionRows = dashboard?.ingestionRows?.length ? dashboard.ingestionRows : defaultIngestionRows;
  const auditRows = dashboard?.auditRows?.length ? dashboard.auditRows : defaultAuditRows;
  const riskBars = dashboard?.riskBars?.length ? dashboard.riskBars : [65, 82, 58, 91, 74, 68];
  const findings = dashboard?.findings?.length ? dashboard.findings : defaultFindings;
  const deliverables = dashboard?.deliverables?.length ? dashboard.deliverables : [
    ['Audit pack', 'WP-514', 'Ready'],
    ['Corrected model', 'XLSX', 'Ready'],
    ['Evidence trail', 'ZIP', 'Ready'],
    ['Board memo', 'PDF', 'Draft'],
  ];

  return (
    <div className="space-y-5 text-slate-100">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-sky-300">
            <Sparkles className="h-3.5 w-3.5" />
            Performance overview
          </div>
          <h2 className="text-2xl font-semibold text-white">
            {engagement.clientName}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('execution')}
            className="rounded-lg border border-sky-500/30 bg-sky-500/10 px-3 py-2 text-xs font-semibold text-sky-200 shadow-[0_0_18px_rgba(56,189,248,0.16)] transition hover:bg-sky-500/20"
          >
            Run assurance suite
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('reporting')}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs font-semibold text-slate-200 transition hover:border-slate-500"
          >
            Export deliverables
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        {overviewCards.map(({ key, Icon, label, accent, title, value, meta, detail, cta }) => (
          <button
            key={key}
            type="button"
            onClick={() => setActiveTab(key)}
            className="group rounded-2xl border border-slate-800 bg-[#0f172a]/90 p-4 text-left shadow-lg shadow-slate-950/20 transition hover:-translate-y-0.5 hover:border-slate-700"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className={`flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.18em] ${accent}`}>
                <Icon className="h-3.5 w-3.5" />
                {label}
              </span>
              <span className="text-[10px] font-medium text-slate-400">{value}</span>
            </div>
            <div className="text-sm font-semibold text-white">{title}</div>
            <div className="mt-4 text-2xl font-bold text-white">{detail}</div>
            <div className="mt-1 text-[11px] text-slate-400">{meta}</div>
            <div className="mt-4 flex items-center justify-between border-t border-slate-800 pt-3 text-[11px] text-slate-300">
              <span>{cta}</span>
              <ChevronRight className="h-3.5 w-3.5 text-slate-500 transition group-hover:translate-x-0.5 group-hover:text-sky-300" />
            </div>
          </button>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Data & ingestion dashboard</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Source quality overview</h3>
            </div>
            <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-semibold text-emerald-300">Operational</span>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
              <div className="mb-3 flex items-center justify-between text-[11px] text-slate-400">
                <span>Record coverage</span>
                <span className="font-semibold text-slate-200">2.43M</span>
              </div>
              <div className="space-y-3">
                {ingestionRows.map(([label, value, state]) => (
                  <div key={label}>
                    <div className="mb-1 flex items-center justify-between text-[11px] text-slate-300">
                      <span>{label}</span>
                      <span className={state === 'Healthy' ? 'text-emerald-300' : state === 'Review' ? 'text-amber-300' : 'text-sky-300'}>{value}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-gradient-to-r from-sky-500 via-cyan-500 to-emerald-400" style={{ width: value }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
              <div className="mb-3 flex items-center justify-between text-[11px] text-slate-400">
                <span>Risk posture</span>
                <span className="font-semibold text-slate-200">Review required</span>
              </div>
              <div className="flex items-end gap-2 pt-4">
                {riskBars.map((value, index) => (
                  <div key={index} className="flex flex-1 flex-col items-center gap-2">
                    <div className="w-full rounded-t-lg bg-gradient-to-t from-sky-500 via-cyan-500 to-emerald-400/80" style={{ height: `${value}%` }} />
                    <span className="text-[10px] text-slate-500">{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][index]}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Financial pulse</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Liquidity snapshot</h3>
            </div>
            <div className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-semibold text-emerald-300">
              <ArrowUpRight className="h-3 w-3" />
              +6.2%
            </div>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                <div className="text-[10px] uppercase tracking-[0.18em] text-slate-400">Cash runway</div>
                <div className="mt-2 text-2xl font-bold text-white">{summary.cashRunwayMonths.toFixed(1)} <span className="text-base text-slate-400">mo</span></div>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                <div className="text-[10px] uppercase tracking-[0.18em] text-slate-400">Current ratio</div>
                <div className="mt-2 text-2xl font-bold text-white">{summary.currentRatio.toFixed(2)} <span className="text-base text-slate-400">x</span></div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
              <div className="mb-3 flex items-center justify-between text-[11px] text-slate-400">
                <span>Key metrics</span>
                <span className="text-slate-200">Target</span>
              </div>
              <div className="space-y-3">
                {[
                  ['Operating margin', `${summary.operatingMarginPct.toFixed(1)}%`, '>= 15%'],
                  ['Net income', `$${summary.netIncome.toLocaleString()}`, '> $2.5M'],
                  ['Cash on hand', `$${summary.liquidCash.toLocaleString()}`, '> $10M'],
                ].map(([label, value, target]) => (
                  <div key={label} className="flex items-center justify-between gap-3 text-[11px] text-slate-300">
                    <span>{label}</span>
                    <div className="flex items-center gap-3">
                      <span className="font-semibold text-white">{value}</span>
                      <span className="text-slate-500">{target}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Audit execution</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Procedure completion</h3>
            </div>
            <button type="button" onClick={() => setActiveTab('execution')} className="text-xs font-semibold text-sky-300">Open suite</button>
          </div>
          <div className="space-y-3">
            {auditRows.map(([label, progress, status]) => (
              <div key={label} className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                <div className="mb-2 flex items-center justify-between text-[11px] text-slate-300">
                  <span>{label}</span>
                  <span className={status === 'FLAGGED' ? 'text-amber-300' : status === 'WATCH' ? 'text-sky-300' : 'text-emerald-300'}>{status}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-sky-500 to-cyan-400" style={{ width: progress }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-4">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Findings</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Risk radar</h3>
            </div>
            <span className="rounded-full bg-red-500/10 px-2 py-1 text-[10px] font-semibold text-red-300">3 open</span>
          </div>
          <div className="space-y-3">
            {findings.map((item) => (
              <div key={item.name} className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-sm font-medium text-white">{item.name}</div>
                    <div className="mt-1 text-[11px] text-slate-400">{item.owner}</div>
                  </div>
                  <span className={`rounded-full px-2 py-1 text-[10px] font-semibold ${item.severity === 'Critical' ? 'bg-red-500/10 text-red-300' : item.severity === 'High' ? 'bg-amber-500/10 text-amber-300' : 'bg-sky-500/10 text-sky-300'}`}>
                    {item.severity}
                  </span>
                </div>
                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                  <span>{item.status}</span>
                  <button type="button" onClick={() => setActiveTab('findings')} className="text-sky-300">Review</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-4">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Reporting summary</p>
            <h3 className="mt-1 text-lg font-semibold text-white">Deliverable readiness</h3>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-emerald-300">
            <Activity className="h-3.5 w-3.5" /> 4 deliverables ready
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          {deliverables.map(([title, value, state]) => (
            <div key={title} className="rounded-xl border border-slate-800 bg-slate-950/40 p-3">
              <div className="text-[11px] uppercase tracking-[0.18em] text-slate-400">{title}</div>
              <div className="mt-3 text-xl font-bold text-white">{value}</div>
              <div className={`mt-3 text-[11px] ${state === 'Ready' ? 'text-emerald-300' : 'text-amber-300'}`}>{state}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
