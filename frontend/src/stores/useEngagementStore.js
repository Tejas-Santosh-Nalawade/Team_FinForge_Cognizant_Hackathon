import { create } from 'zustand';
import { runScenarioSimulation, resolveDiscrepancies, fetchDashboardSummary } from '../api/client';

const displayValue = (value, fallback = 'Not provided') => {
  if (typeof value !== 'number') return fallback;
  return Math.abs(value) >= 1000 ? `$${value.toLocaleString()}` : value.toFixed(2);
};

const findingFromAuditResult = (finding, index) => ({
  id: finding.id || `FINDING-${String(index + 1).padStart(3, '0')}`,
  rule_id: finding.rule_id || finding.reference || finding.category || `RULE_${index + 1}`,
  title: finding.description || finding.procedure || 'Audit exception requiring review',
  category: finding.category || 'Audit assurance',
  severity: finding.severity || 'High',
  actual: displayValue(finding.actual ?? finding.submitted_value),
  expected: displayValue(finding.expected ?? finding.expected_value),
  variance: displayValue(finding.difference ?? finding.variance_amount, 'Review required'),
  status: finding.status === 'PASS' ? 'RESOLVED' : 'OPEN',
  workingPaper: finding.evidence || `WP-${String(index + 1).padStart(3, '0')}`,
  detectedOn: finding.lastRun || new Date().toISOString().slice(0, 10),
  impact: finding.issue || finding.audit_notes || 'Review supporting evidence and resolve the exception.',
  materiality: 'Pending assessment',
  rootCause: finding.issue || 'Use the RAG advisor to retrieve the relevant policy context and remediation guidance.',
  ascIfrsReference: 'Select “Ask AI & RAG Advisor” to retrieve the applicable source excerpts.',
  recommendedResolution: finding.resolution || 'Document the conclusion, post an AJE if needed, or record an approved waiver.',
  resolutionDecision: finding.resolution_status || 'UNRESOLVED',
  notes: finding.audit_notes || '',
  submittedValue: finding.submitted_value,
  expectedValue: finding.expected_value,
});

export const useEngagementStore = create((set, get) => ({
  // Session state is deliberately kept in sessionStorage so a browser close
  // clears local demo access while a normal refresh preserves the workspace.
  session: (() => {
    if (typeof window === 'undefined') return { authenticated: false, user: null };
    try {
      return JSON.parse(window.sessionStorage.getItem('finforge_session')) || { authenticated: false, user: null };
    } catch {
      return { authenticated: false, user: null };
    }
  })(),
  startSession: async (loginResult) => {
    const session = { authenticated: true, user: loginResult.user };
    window.sessionStorage.setItem('finforge_access_token', loginResult.access_token);
    window.sessionStorage.setItem('finforge_session', JSON.stringify(session));
    set({ session });
    try {
      await get().loadDashboardSnapshot();
    } catch (error) {
      console.warn('Unable to hydrate dashboard via API; using local defaults.', error);
    }
  },
  endSession: () => {
    window.sessionStorage.removeItem('finforge_access_token');
    window.sessionStorage.removeItem('finforge_session');
    set({ session: { authenticated: false, user: null } });
  },

  // Navigation
  activeTab: 'planning', // planning | ingestion | analytics | execution | findings | simulator | reporting | closure
  setActiveTab: (tab) => set({ activeTab: tab }),

  // Engagement Information
  engagement: {
    id: 'ENG-2025-514',
    clientName: 'Apex Global Technologies Inc.',
    periodEnding: '2025-12-31',
    framework: 'US GAAP / IFRS',
    reviewStage: 'CY_DRAFT_FS',
    riskStatus: 'REVIEW_REQUIRED', // CLEAN | CORRECTED | WAIVED_RISK | REVIEW_REQUIRED
    overallMateriality: 440000.0,
    performanceMateriality: 330000.0,
    trivialThreshold: 22000.0,
    planningMateriality: 440000.0,
  },
  setEngagement: (eng) => set((state) => ({ engagement: { ...state.engagement, ...eng } })),

  // Risk Banner State
  riskBanner: {
    active: false,
    message: 'WARNING: 1 or more mathematical tie-out errors were waived by the user. Analytics may be distorted.',
  },
  setRiskBanner: (active, message) =>
    set({
      riskBanner: {
        active,
        message: message || 'WARNING: 1 or more mathematical tie-out errors were waived by the user. Analytics may be distorted.',
      },
    }),

  dashboard: {
    overviewCards: [],
    ingestionRows: [],
    auditRows: [],
    riskBars: [],
    findings: [],
    deliverables: [],
  },
  loadDashboardSnapshot: async (engagementId) => {
    try {
      const payload = await fetchDashboardSummary(engagementId || get().engagement.id);
      const engagement = payload?.engagement || {};
      const summary = payload?.summary || {};
      set((state) => ({
        engagement: {
          ...state.engagement,
          ...engagement,
          id: engagement.id || state.engagement.id,
          clientName: engagement.clientName || state.engagement.clientName,
          periodEnding: engagement.periodEnding || state.engagement.periodEnding,
          framework: engagement.framework || state.engagement.framework,
          reviewStage: engagement.reviewStage || state.engagement.reviewStage,
          riskStatus: engagement.riskStatus || state.engagement.riskStatus,
          overallMateriality: engagement.overallMateriality ?? state.engagement.overallMateriality,
          performanceMateriality: engagement.performanceMateriality ?? state.engagement.performanceMateriality,
          trivialThreshold: engagement.trivialThreshold ?? state.engagement.trivialThreshold,
          planningMateriality: engagement.planningMateriality ?? state.engagement.planningMateriality,
        },
        summary: {
          ...state.summary,
          ...summary,
        },
        dashboard: {
          overviewCards: payload?.overviewCards || state.dashboard.overviewCards,
          ingestionRows: payload?.ingestionRows || state.dashboard.ingestionRows,
          auditRows: payload?.auditRows || state.dashboard.auditRows,
          riskBars: payload?.riskBars || state.dashboard.riskBars,
          findings: payload?.findings || state.dashboard.findings,
          deliverables: payload?.deliverables || state.dashboard.deliverables,
        },
      }));
      return payload;
    } catch (error) {
      console.warn('Dashboard summary unavailable; falling back to local seed data.', error);
      return null;
    }
  },

  // Procedures Matrix (56 Rules)
  procedures: [
    { step: 1, reference: 'MATH_01', category: 'Internal Consistency', procedure: 'Arithmetic Integrity - Trial Balance', severity: 'Critical', status: 'PASS', evidence: 'WP-101', lastRun: '2025-06-02' },
    { step: 2, reference: 'MATH_02', category: 'Internal Consistency', procedure: 'Total Assets = Liabilities + Equity', severity: 'Critical', status: 'PASS', evidence: 'WP-102', lastRun: '2025-06-02' },
    { step: 3, reference: 'MATH_03', category: 'Internal Consistency', procedure: 'Net Income ties to Retained Earnings', severity: 'Critical', status: 'PASS', evidence: 'WP-103', lastRun: '2025-06-02' },
    { step: 4, reference: 'RATIO_01', category: 'Liquidity Ratios', procedure: 'Current Ratio > 1.50x', severity: 'High', status: 'PASS', evidence: 'WP-201', lastRun: '2025-06-02' },
    { step: 5, reference: 'RATIO_02', category: 'Liquidity Ratios', procedure: 'Quick Ratio > 1.00x', severity: 'High', status: 'FLAGGED', evidence: 'WP-202', lastRun: '2025-06-02' },
    { step: 6, reference: 'RATIO_03', category: 'Liquidity Ratios', procedure: 'Cash Runway > 12 Months', severity: 'Critical', status: 'FLAGGED', evidence: 'WP-203', lastRun: '2025-06-02' },
    { step: 7, reference: 'RATIO_04', category: 'Profitability Ratios', procedure: 'Operating Margin > 15%', severity: 'High', status: 'PASS', evidence: 'WP-204', lastRun: '2025-06-02' },
    { step: 8, reference: 'RATIO_05', category: 'Profitability Ratios', procedure: 'Net Margin > 8%', severity: 'Medium', status: 'PASS', evidence: 'WP-205', lastRun: '2025-06-02' },
    { step: 9, reference: 'TIEOUT_01', category: 'Cross-Statement Tie-Out', procedure: 'Ending Cash (CFS) ties to BS Cash', severity: 'Critical', status: 'PASS', evidence: 'WP-301', lastRun: '2025-06-02' },
    { step: 10, reference: 'TIEOUT_02', category: 'Cross-Statement Tie-Out', procedure: 'Net Income (IS) ties to CFS Net Income', severity: 'Critical', status: 'PASS', evidence: 'WP-302', lastRun: '2025-06-02' },
    { step: 11, reference: 'NOTE_01', category: 'Disclosure & Footnotes', procedure: 'AR Aging Gross ties to BS Accounts Receivable', severity: 'High', status: 'PASS', evidence: 'WP-401', lastRun: '2025-06-02' },
    { step: 12, reference: 'NOTE_02', category: 'Disclosure & Footnotes', procedure: 'Allowance for Credit Losses (CECL Provision)', severity: 'Critical', status: 'PASS', evidence: 'WP-402', lastRun: '2025-06-02' },
    { step: 13, reference: 'NOTE_03', category: 'Disclosure & Footnotes', procedure: 'PP&E Net Roll-forward ties to BS Fixed Assets', severity: 'High', status: 'PASS', evidence: 'WP-403', lastRun: '2025-06-02' },
    { step: 14, reference: 'NOTE_07', category: 'Disclosure & Footnotes', procedure: 'Debt Maturity Schedule aggregate ties to Total Debt', severity: 'High', status: 'PASS', evidence: 'WP-404', lastRun: '2025-06-02' },
  ],
  setProcedures: (procs) => set({ procedures: procs }),

  // Summary Metrics
  summary: {
    totalProcedures: 56,
    passedProcedures: 54,
    flaggedProcedures: 2,
    passScorePct: 96.4,
    cashRunwayMonths: 8.4,
    quickRatio: 0.88,
    currentRatio: 5.75,
    operatingMarginPct: 13.8,
    operatingTurnover: 22000000.0,
    grossProfit: 11500000.0,
    netIncome: 2760000.0,
    liquidCash: 12450000.0,
    totalAssets: 24800000.0,
    totalLiabilities: 8700000.0,
    debtMaturity12Mo: 3200000.0,
  },
  setSummary: (sum) => set((state) => ({ summary: { ...state.summary, ...sum } })),

  hydrateAuditRun: (result) => {
    const meta = result.engagement || {};
    const importedFindings = (result.findings || []).map(findingFromAuditResult);
    const total = result.total_procedures || 56;
    const passed = result.passed_count ?? 0;
    set((state) => ({
      engagement: {
        ...state.engagement,
        id: result.engagement_id || state.engagement.id,
        clientName: meta.client_name || state.engagement.clientName,
        periodEnding: meta.period_ending || state.engagement.periodEnding,
        framework: meta.framework || state.engagement.framework,
        reviewStage: meta.review_stage || state.engagement.reviewStage,
        riskStatus: result.risk_status || state.engagement.riskStatus,
        overallMateriality: meta.overall_materiality || state.engagement.overallMateriality,
        performanceMateriality: meta.performance_materiality || state.engagement.performanceMateriality,
        trivialThreshold: meta.trivial_threshold || state.engagement.trivialThreshold,
      },
      procedures: result.procedures || state.procedures,
      findings: importedFindings.length ? importedFindings : state.findings,
      selectedFinding: importedFindings[0] || state.selectedFinding,
      summary: {
        ...state.summary,
        totalProcedures: total,
        passedProcedures: passed,
        flaggedProcedures: result.flagged_count ?? Math.max(total - passed, 0),
        passScorePct: total ? Math.round((passed / total) * 1000) / 10 : 0,
      },
    }));
  },

  // Findings List
  findings: [
    {
      id: 'FINDING-001',
      rule_id: 'RATIO_02',
      title: 'Quick Ratio Below Compliance Threshold',
      category: 'Liquidity Ratios',
      severity: 'Critical',
      actual: '0.88x',
      expected: '> 1.00x',
      variance: '-12.0%',
      status: 'OPEN',
      workingPaper: 'WP-202',
      detectedOn: '2025-06-02',
      impact: 'Potential liquidity risk during debt service window',
      materiality: '$105,000',
      rootCause: 'Increase in short-term liabilities and decrease in highly liquid assets contributed to the Quick Ratio falling below the acceptable threshold.',
      ascIfrsReference: 'ASC 210-10-45-16 (Current Assets - Quick Assets)\n"Quick assets generally include cash, marketable securities, and accounts receivable that can be converted to cash within 90 days. Entities shall classify assets based on their liquidity and availability for current obligations."',
      recommendedResolution: 'Review short-term liability management and optimize cash conversion cycle. Improve receivables collection timeline and maintain higher cash reserves.',
      resolutionDecision: 'UNRESOLVED', // ACCEPTED | WAIVED
      notes: '',
    },
    {
      id: 'FINDING-002',
      rule_id: 'RATIO_03',
      title: 'Cash Runway Below 12-Month Threshold',
      category: 'Liquidity Ratios',
      severity: 'Critical',
      actual: '8.4 Mo',
      expected: '> 12.0 Mo',
      variance: '-30.0%',
      status: 'OPEN',
      workingPaper: 'WP-203',
      detectedOn: '2025-06-02',
      impact: 'Operating cash depletion within 3 fiscal quarters',
      materiality: '$350,000',
      rootCause: 'Accelerated R&D headcount expenditures outpaced gross margin conversion.',
      ascIfrsReference: 'ASC 205-40 (Going Concern Assessment)\n"Management must evaluate whether there is substantial doubt about the entity\'s ability to continue as a going concern within one year after the financial statement issuance date."',
      recommendedResolution: 'Implement OpEx rationalization program or draw on revolving credit facility.',
      resolutionDecision: 'UNRESOLVED',
      notes: '',
    },
  ],
  selectedFinding: null,
  setSelectedFinding: (finding) => set({ selectedFinding: finding }),

  // Simulator Drivers
  simulator: {
    salesVolumeDeltaPct: 5.0,
    pricingDeltaPct: 5.0,
    interestRateDeltaPct: 10.0,
    operatingCostsDeltaPct: 55.0,
    simulatedCashRunwayMonths: 5.6,
    deltaVsBaselineMonths: -2.8,
    projectedEndingCash: 4100000.0,
    netImpactPct: -24.5,
    trajectoryPoints: [
      { month: 'Jan', baseline_cash_m: 12.45, simulated_cash_m: 12.45 },
      { month: 'Feb', baseline_cash_m: 12.1, simulated_cash_m: 11.6 },
      { month: 'Mar', baseline_cash_m: 11.8, simulated_cash_m: 10.8 },
      { month: 'Apr', baseline_cash_m: 11.4, simulated_cash_m: 9.9 },
      { month: 'May', baseline_cash_m: 11.0, simulated_cash_m: 9.1 },
      { month: 'Jun', baseline_cash_m: 10.6, simulated_cash_m: 8.3 },
      { month: 'Jul', baseline_cash_m: 10.2, simulated_cash_m: 7.5 },
      { month: 'Aug', baseline_cash_m: 9.8, simulated_cash_m: 6.7 },
      { month: 'Sep', baseline_cash_m: 9.4, simulated_cash_m: 5.9 },
      { month: 'Oct', baseline_cash_m: 9.0, simulated_cash_m: 5.1 },
      { month: 'Nov', baseline_cash_m: 8.7, simulated_cash_m: 4.6 },
      { month: 'Dec', baseline_cash_m: 8.4, simulated_cash_m: 4.1 },
    ],
  },
  setSimulatorDrivers: (drivers) =>
    set((state) => ({ simulator: { ...state.simulator, ...drivers } })),

  // Actions
  resolveFindingAction: async (findingId, decision, notes) => {
    const selected = get().findings.find((finding) => finding.id === findingId);
    const findings = get().findings.map((f) => {
      if (f.id === findingId) {
        return { ...f, resolutionDecision: decision, status: decision === 'ACCEPTED' ? 'RESOLVED' : 'WAIVED', notes };
      }
      return f;
    });

    const anyWaived = findings.some((f) => f.resolutionDecision === 'WAIVED');
    const allResolved = findings.every((f) => f.resolutionDecision !== 'UNRESOLVED');

    set({
      findings,
      riskBanner: {
        active: anyWaived,
        message: anyWaived ? 'WARNING: 1 or more mathematical tie-out errors were waived by the user. Analytics may be distorted.' : '',
      },
      engagement: {
        ...get().engagement,
        riskStatus: anyWaived ? 'WAIVED_RISK' : allResolved ? 'CORRECTED' : 'REVIEW_REQUIRED',
      },
    });

    // Persist only the decision the auditor just made.  Sending every unresolved
    // row as WAIVED would create a false risk escalation in the audit ledger.
    try {
      const response = await resolveDiscrepancies({
        engagement_id: get().engagement.id,
        decisions: [{
          rule_id: selected?.rule_id || findingId,
          decision,
          notes,
          submitted_value: selected?.submittedValue,
          expected_value: selected?.expectedValue,
        }],
      });
      set((state) => ({
        engagement: { ...state.engagement, riskStatus: response.risk_status || state.engagement.riskStatus },
        riskBanner: {
          active: Boolean(response.risk_banner_active),
          message: response.risk_banner_message || state.riskBanner.message,
        },
      }));
    } catch (e) {
      console.warn('Resolution remains in local demonstration state until an engagement is ingested.', e);
    }
  },

  updateSimulator: async (drivers) => {
    const updated = { ...get().simulator, ...drivers };
    set({ simulator: updated });

    try {
      const res = await runScenarioSimulation({
        sales_volume_delta_pct: updated.salesVolumeDeltaPct,
        pricing_delta_pct: updated.pricingDeltaPct,
        interest_rate_delta_pct: updated.interestRateDeltaPct,
        operating_costs_delta_pct: updated.operatingCostsDeltaPct,
      });
      if (res && res.status === 'success') {
        set({
          simulator: {
            ...updated,
            simulatedCashRunwayMonths: res.simulated_cash_runway_months,
            deltaVsBaselineMonths: res.delta_runway_months,
            projectedEndingCash: res.projected_ending_cash,
            netImpactPct: res.net_impact_pct,
            trajectoryPoints: res.trajectory_points,
          },
        });
      }
    } catch (e) {
      console.log('Using deterministic frontend simulation curve');
    }
  },
}));
