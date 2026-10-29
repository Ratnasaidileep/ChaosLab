import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { OverviewSection } from './components/OverviewSection';
import { ServiceHealthSection } from './components/ServiceHealthSection';
import { FailureInjectionSection } from './components/FailureInjectionSection';
import { ExperimentHistorySection } from './components/ExperimentHistorySection';
import { RecoveryAnalysisSection } from './components/RecoveryAnalysisSection';
import {
  DashboardSummary,
  RecoveryAnalysisData,
  ServiceHealth,
  Experiment,
  ExperimentType,
  TargetService
} from './types';
import { api } from './api';
import { AlertCircle, CheckCircle2, X } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [analysis, setAnalysis] = useState<RecoveryAnalysisData | null>(null);
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [experiments, setExperiments] = useState<Experiment[]>([]);

  const [notification, setNotification] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

  const [isTriggering, setIsTriggering] = useState<boolean>(false);
  const [isCancelling, setIsCancelling] = useState<boolean>(false);

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification((curr) => (curr?.message === message ? null : curr));
    }, 5000);
  };

  const loadData = useCallback(async () => {
    try {
      const summaryData = await api.getDashboardSummary();
      setSummary(summaryData);
      setServices(Object.values(summaryData.services));

      const exps = await api.getExperiments({ limit: 50 });
      setExperiments(exps);

      const analysisData = await api.getRecoveryAnalysis();
      setAnalysis(analysisData);
    } catch (err: any) {
      console.warn('Polling error:', err);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleTriggerExperiment = async (payload: {
    type: ExperimentType;
    target_service: TargetService;
    duration_seconds: number;
    load_percent?: number;
    memory_mb?: number;
    delay_ms?: number;
    confirm_destruction: boolean;
  }) => {
    setIsTriggering(true);
    try {
      const exp = await api.triggerExperiment(payload);
      showNotification(
        'success',
        `Chaos Experiment [${exp.id}] injected on ${payload.target_service}!`
      );
      await loadData();
      setActiveTab('overview');
    } catch (err: any) {
      showNotification('error', `Failed to inject experiment: ${err.message}`);
      throw err;
    } finally {
      setIsTriggering(false);
    }
  };

  const handleCancelExperiment = async (id: string) => {
    setIsCancelling(true);
    try {
      await api.cancelExperiment(id);
      showNotification('info', `Cancellation requested for experiment [${id}]. Recovering...`);
      await loadData();
    } catch (err: any) {
      showNotification('error', `Failed to cancel experiment: ${err.message}`);
    } finally {
      setIsCancelling(false);
    }
  };

  const handleVerifyService = async (serviceId: string) => {
    try {
      const res = await api.verifyService(serviceId);
      if (res.verified) {
        showNotification('success', `Health check verified for ${serviceId}: HEALTHY`);
      } else {
        showNotification('error', `Health verification failed for ${serviceId}: ${res.details?.error || 'UNHEALTHY'}`);
      }
      await loadData();
    } catch (err: any) {
      showNotification('error', `Verification request failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealth={summary?.overall_system_health || 'HEALTHY'}
      />

      {/* Floating Notification Toast */}
      {notification && (
        <div className="fixed bottom-5 right-5 z-50 animate-in slide-in-from-bottom-5 duration-200">
          <div
            className={`flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-2xl border text-xs font-medium backdrop-blur-md ${
              notification.type === 'success'
                ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200'
                : notification.type === 'error'
                ? 'bg-rose-950/90 border-rose-500/40 text-rose-200'
                : 'bg-cyan-950/90 border-cyan-500/40 text-cyan-200'
            }`}
          >
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="ml-2 text-slate-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <OverviewSection
            summary={summary}
            onNavigateToInjection={() => setActiveTab('injection')}
            onNavigateToHistory={() => setActiveTab('history')}
            onCancelActiveExperiment={handleCancelExperiment}
            isCancelling={isCancelling}
          />
        )}

        {activeTab === 'services' && (
          <ServiceHealthSection
            services={services}
            onVerifyService={handleVerifyService}
          />
        )}

        {activeTab === 'injection' && (
          <FailureInjectionSection
            onTriggerExperiment={handleTriggerExperiment}
            isTriggering={isTriggering}
          />
        )}

        {activeTab === 'history' && (
          <ExperimentHistorySection
            experiments={experiments}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'analysis' && (
          <RecoveryAnalysisSection
            analysis={analysis}
            onNavigateToInjection={() => setActiveTab('injection')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-6 text-center text-xs text-slate-500 font-mono">
        <p>ChaosLab &bull; Automated Failure Injection & Resilience Recovery Platform</p>
        <p className="mt-1 text-[11px] text-slate-600">Built for DevOps & Reliability Engineering</p>
      </footer>
    </div>
  );
}

export default App;
