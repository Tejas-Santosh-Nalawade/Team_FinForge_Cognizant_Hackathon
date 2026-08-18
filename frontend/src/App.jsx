import React from 'react';
import { useEngagementStore } from './stores/useEngagementStore';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { RiskBanner } from './components/layout/RiskBanner';
import { PlanningDashboard } from './pages/PlanningDashboard';
import { IngestionDashboard } from './pages/IngestionDashboard';
import { AnalyticalDashboard } from './pages/AnalyticalDashboard';
import { AuditExecutionDashboard } from './pages/AuditExecutionDashboard';
import { FindingsDashboard } from './pages/FindingsDashboard';
import { SimulatorDashboard } from './pages/SimulatorDashboard';
import { ReportingDashboard } from './pages/ReportingDashboard';
import { ClosureDashboard } from './pages/ClosureDashboard';
import { LoginScreen } from './components/auth/LoginScreen';

function App() {
  const { activeTab, session } = useEngagementStore();

  if (!session.authenticated) return <LoginScreen />;

  const renderActiveView = () => {
    switch (activeTab) {
      case 'planning':
        return <PlanningDashboard />;
      case 'ingestion':
        return <IngestionDashboard />;
      case 'analytics':
        return <AnalyticalDashboard />;
      case 'execution':
        return <AuditExecutionDashboard />;
      case 'findings':
        return <FindingsDashboard />;
      case 'simulator':
        return <SimulatorDashboard />;
      case 'reporting':
        return <ReportingDashboard />;
      case 'closure':
        return <ClosureDashboard />;
      default:
        return <PlanningDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
      {/* Persistent High Risk Warning Banner */}
      <RiskBanner />

      {/* Global Top Header Bar with Stepper and Quick Actions */}
      <Header />

      {/* Main Layout Body: Sidebar + Active View Container */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />

        <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto w-full">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
