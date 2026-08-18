import React, { useState } from 'react';
import { ArrowRight, BrainCircuit, LockKeyhole, ShieldCheck, Sparkles } from 'lucide-react';
import { loginToWorkspace } from '../../api/client';
import { useEngagementStore } from '../../stores/useEngagementStore';

export const LoginScreen = () => {
  const startSession = useEngagementStore((state) => state.startSession);
  const [email, setEmail] = useState('auditor@apexglobal.com');
  const [password, setPassword] = useState('FinForge!2026');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');
    try {
      startSession(await loginToWorkspace(email, password));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to reach the secure workspace. Start the API and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#060b18] px-5 py-10 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_22%,rgba(56,189,248,0.18),transparent_30%),radial-gradient(circle_at_82%_18%,rgba(129,140,248,0.18),transparent_28%),radial-gradient(circle_at_55%_88%,rgba(16,185,129,0.12),transparent_35%)]" />
      <div className="pointer-events-none absolute inset-0 opacity-30 [background-image:linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px)] [background-size:48px_48px]" />

      <div className="relative mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-10 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="max-w-2xl">
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-semibold tracking-wide text-sky-200">
            <Sparkles className="h-3.5 w-3.5" />
            Financial intelligence, grounded in evidence
          </div>
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 via-indigo-500 to-cyan-300 text-xl font-black text-white shadow-lg shadow-sky-500/20">F</div>
            <div>
              <div className="text-lg font-bold tracking-tight text-white">FinForge</div>
              <div className="text-xs text-slate-400">FP&amp;A Audit Assurance Suite</div>
            </div>
          </div>
          <h1 className="max-w-xl text-4xl font-semibold leading-tight tracking-tight text-white sm:text-5xl">
            From financial data to <span className="bg-gradient-to-r from-sky-300 to-emerald-300 bg-clip-text text-transparent">defensible assurance.</span>
          </h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-slate-300">
            A guided audit workspace for planning, validation, financial insight, documented remediation, and evidence-backed reporting.
          </p>
          <div className="mt-9 grid gap-3 sm:grid-cols-3">
            {[
              ['56', 'Deterministic controls'],
              ['RAG', 'Source-grounded advisory'],
              ['1', 'Connected evidence trail'],
            ].map(([metric, label]) => (
              <div key={metric} className="rounded-xl border border-white/10 bg-white/[0.045] p-3 backdrop-blur">
                <div className="text-lg font-bold text-white">{metric}</div>
                <div className="text-[11px] text-slate-400">{label}</div>
              </div>
            ))}
          </div>
          <div className="mt-8 flex flex-wrap gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1.5"><ShieldCheck className="h-4 w-4 text-emerald-400" /> Role-aware audit workspace</span>
            <span className="flex items-center gap-1.5"><BrainCircuit className="h-4 w-4 text-violet-400" /> Human-reviewed AI advisory</span>
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-black/30 backdrop-blur-xl sm:p-8">
          <div className="mb-7 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-300">Secure workspace</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Welcome back</h2>
              <p className="mt-1 text-sm text-slate-400">Sign in to continue your assurance workflow.</p>
            </div>
            <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 p-2.5"><LockKeyhole className="h-5 w-5 text-emerald-300" /></div>
          </div>
          <form className="space-y-4" onSubmit={submit}>
            <label className="block text-xs font-medium text-slate-300">
              Work email
              <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required className="mt-1.5 w-full rounded-xl border border-slate-700 bg-slate-900/90 px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-sky-400 focus:ring-2 focus:ring-sky-400/15" />
            </label>
            <label className="block text-xs font-medium text-slate-300">
              Password
              <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required className="mt-1.5 w-full rounded-xl border border-slate-700 bg-slate-900/90 px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-sky-400 focus:ring-2 focus:ring-sky-400/15" />
            </label>
            {error && <p className="rounded-lg border border-red-800/60 bg-red-950/40 px-3 py-2 text-xs text-red-200">{error}</p>}
            <button disabled={isSubmitting} type="submit" className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 transition hover:from-sky-400 hover:to-indigo-400 disabled:cursor-not-allowed disabled:opacity-60">
              {isSubmitting ? 'Authenticating…' : 'Enter assurance workspace'} <ArrowRight className="h-4 w-4" />
            </button>
          </form>
          <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-[11px] leading-5 text-slate-400">
            <span className="font-semibold text-slate-300">Local demo access:</span> credentials above are seeded only for development. Configure the environment variables before deployment.
          </div>
        </section>
      </div>
    </main>
  );
};
