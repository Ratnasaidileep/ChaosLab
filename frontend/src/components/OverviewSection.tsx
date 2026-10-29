import React from 'react';
import {
  ShieldCheck,
  Server,
  ShoppingCart,
  Flame,
  CheckCircle2,
  XCircle,
  Clock,
  Ban,
  ArrowRight,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { DashboardSummary, Experiment } from '../types';
import { MetricCard } from './MetricCard';

interface OverviewSectionProps {
  summary: DashboardSummary | null;
  onNavigateToInjection: () => void;
  onNavigateToHistory: () => void;
  onCancelActiveExperiment: (id: string) => void;
  isCancelling?: boolean;
}

export const OverviewSection: React.FC<OverviewSectionProps> = ({
  summary,
  onNavigateToInjection,
  onNavigateToHistory,
  onCancelActiveExperiment,
  isCancelling = false,
}) => {
  if (!summary) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 text-slate-400 font-mono text-sm">
          <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          Loading ChaosLab telemetry...
        </div>
      </div>
    );
  }

  const active = summary.active_experiment;

  const getSystemHealthBadge = () => {
    switch (summary.overall_system_health) {
      case 'HEALTHY':
        return { text: 'Optimal', variant: 'success' as const };
      case 'DEGRADED':
        return { text: 'Degraded', variant: 'warning' as const };
      case 'UNHEALTHY':
        return { text: 'Critical', variant: 'danger' as const };
    }
  };

  const getServiceStatusBadge = (status: string) => {
    switch (status) {
      case 'HEALTHY':
        return { text: 'Healthy', variant: 'success' as const };
      case 'DEGRADED':
        return { text: 'Degraded', variant: 'warning' as const };
      default:
        return { text: 'Failed', variant: 'danger' as const };
    }
  };

  const formatMs = (ms: number | null) => {
    if (ms === null || ms === undefined) return 'N/A';
    if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
    return `${Math.round(ms)}ms`;
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Active Experiment Live Progress Banner */}
      {active && (
        <div className="bg-gradient-to-r from-rose-950/40 via-slate-900 to-slate-900 border border-rose-500/40 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-rose-500/5 rounded-full blur-3xl pointer-events-none"></div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-rose-500"></span>
              </span>
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  Active Chaos Experiment Running:
                  <span className="text-rose-400 uppercase font-mono tracking-wide">
                    {active.type.replace('_', ' ')}
                  </span>
                </h3>
                <p className="text-xs text-slate-400 font-mono">
                  Target: <span className="text-cyan-400 font-semibold">{active.target_service}</span> &bull; ID: {active.id}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-semibold">
                State: {active.status}
              </span>
              <button
                onClick={() => onCancelActiveExperiment(active.id)}
                disabled={isCancelling}
                className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold text-rose-200 hover:text-white bg-rose-900/60 hover:bg-rose-800/80 border border-rose-700/50 rounded-lg transition"
              >
                <Ban className="w-3.5 h-3.5" />
                {isCancelling ? 'Cancelling...' : 'Cancel Experiment'}
              </button>
            </div>
          </div>

          {/* Stepper Progress */}
          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            {/* Step 1 */}
            <div className={`p-3 rounded-xl border ${
              active.status !== 'PENDING'
                ? 'bg-cyan-950/20 border-cyan-500/40 text-cyan-300'
                : 'bg-slate-900 border-slate-800 text-slate-500'
            }`}>
              <div className="font-semibold text-white flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                1. Injected
              </div>
              <div className="mt-1 text-[11px] text-slate-400 truncate">
                {active.failure_timestamp ? 'Failure Active' : 'Injecting...'}
              </div>
            </div>

            {/* Step 2 */}
            <div className={`p-3 rounded-xl border ${
              ['DETECTED', 'RECOVERING', 'VERIFYING', 'RECOVERED'].includes(active.status)
                ? 'bg-cyan-950/20 border-cyan-500/40 text-cyan-300'
                : 'bg-slate-900 border-slate-800 text-slate-500'
            }`}>
              <div className="font-semibold text-white flex items-center gap-1.5">
                <CheckCircle2 className={`w-3.5 h-3.5 ${active.detection_timestamp ? 'text-cyan-400' : 'text-slate-600'}`} />
                2. Detected
              </div>
              <div className="mt-1 text-[11px] text-slate-400 truncate">
                {active.detection_time_ms ? `In ${formatMs(active.detection_time_ms)}` : 'Monitoring probe...'}
              </div>
            </div>

            {/* Step 3 */}
            <div className={`p-3 rounded-xl border ${
              ['RECOVERING', 'VERIFYING', 'RECOVERED'].includes(active.status)
                ? 'bg-cyan-950/20 border-cyan-500/40 text-cyan-300'
                : 'bg-slate-900 border-slate-800 text-slate-500'
            }`}>
              <div className="font-semibold text-white flex items-center gap-1.5">
                <CheckCircle2 className={`w-3.5 h-3.5 ${active.recovery_start_timestamp ? 'text-cyan-400' : 'text-slate-600'}`} />
                3. Recovering
              </div>
              <div className="mt-1 text-[11px] text-slate-400 truncate">
                {active.recovery_start_timestamp ? 'Restoration Triggered' : 'Waiting duration...'}
              </div>
            </div>

            {/* Step 4 */}
            <div className={`p-3 rounded-xl border ${
              active.status === 'RECOVERED'
                ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
                : 'bg-slate-900 border-slate-800 text-slate-500'
            }`}>
              <div className="font-semibold text-white flex items-center gap-1.5">
                <CheckCircle2 className={`w-3.5 h-3.5 ${active.status === 'RECOVERED' ? 'text-emerald-400' : 'text-slate-600'}`} />
                4. Verified
              </div>
              <div className="mt-1 text-[11px] text-slate-400 truncate">
                {active.status === 'RECOVERED' ? 'Health Restored' : 'Awaiting verification'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top System Health Headline Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">
              Application Under Test: Online Shopping System
            </h2>
            <p className="text-xs text-slate-400">
              Microservices architecture resilience verification suite
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onNavigateToInjection}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white transition shadow-sm shadow-cyan-600/30"
          >
            <Flame className="w-3.5 h-3.5" />
            Launch Experiment
          </button>
          <button
            onClick={onNavigateToHistory}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700"
          >
            View History
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Overall System"
          value={summary.overall_system_health}
          badge={getSystemHealthBadge()}
          icon={ShieldCheck}
          accentColor={
            summary.overall_system_health === 'HEALTHY'
              ? 'emerald'
              : summary.overall_system_health === 'DEGRADED'
              ? 'amber'
              : 'rose'
          }
          subtitle="Real-time multi-service status"
        />

        <MetricCard
          title="Product Service"
          value={summary.services['product-service']?.status || 'DOWN'}
          badge={getServiceStatusBadge(summary.services['product-service']?.status)}
          icon={Server}
          accentColor={
            summary.services['product-service']?.status === 'HEALTHY'
              ? 'emerald'
              : 'rose'
          }
          subtitle={`Latency: ${summary.services['product-service']?.latency_ms || 0}ms`}
        />

        <MetricCard
          title="Order Service"
          value={summary.services['order-service']?.status || 'DOWN'}
          badge={getServiceStatusBadge(summary.services['order-service']?.status)}
          icon={ShoppingCart}
          accentColor={
            summary.services['order-service']?.status === 'HEALTHY'
              ? 'emerald'
              : 'rose'
          }
          subtitle={`Latency: ${summary.services['order-service']?.latency_ms || 0}ms`}
        />

        <MetricCard
          title="Avg Recovery Time"
          value={formatMs(summary.avg_recovery_duration_ms)}
          badge={{ text: 'MTTR', variant: 'info' }}
          icon={Clock}
          accentColor="cyan"
          subtitle={`Avg Downtime: ${formatMs(summary.avg_total_downtime_ms)}`}
        />
      </div>

      {/* Secondary Statistics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Total Experiments"
          value={summary.total_experiments}
          icon={Flame}
          accentColor="blue"
          subtitle="Intentional failure injections run"
        />

        <MetricCard
          title="Successful Recoveries"
          value={summary.successful_recoveries}
          badge={{ text: `${summary.recovery_success_rate_percent}% Rate`, variant: 'success' }}
          icon={CheckCircle2}
          accentColor="emerald"
          subtitle="Services verified healthy after chaos"
        />

        <MetricCard
          title="Failed Recoveries"
          value={summary.failed_recoveries}
          badge={summary.failed_recoveries > 0 ? { text: 'Alert', variant: 'danger' } : undefined}
          icon={XCircle}
          accentColor={summary.failed_recoveries > 0 ? 'rose' : 'cyan'}
          subtitle="Exceeded timeout or unrecovered"
        />
      </div>
    </div>
  );
};
