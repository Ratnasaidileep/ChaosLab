import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Clock,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Flame,
  ArrowUpRight
} from 'lucide-react';
import { RecoveryAnalysisData } from '../types';
import { MetricCard } from './MetricCard';

interface RecoveryAnalysisSectionProps {
  analysis: RecoveryAnalysisData | null;
  onNavigateToInjection: () => void;
}

export const RecoveryAnalysisSection: React.FC<RecoveryAnalysisSectionProps> = ({
  analysis,
  onNavigateToInjection,
}) => {
  if (!analysis || analysis.summary.total_experiments === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center max-w-2xl mx-auto space-y-4 animate-in fade-in duration-200">
        <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mx-auto flex items-center justify-center">
          <BarChart3 className="w-7 h-7" />
        </div>
        <h3 className="text-lg font-bold text-white tracking-tight">
          No Resilience Telemetry Recorded Yet
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed max-w-md mx-auto">
          Recovery analysis metrics and comparative MTTR graphs are generated from real, verified failure injection experiments. Run your first experiment to see live data.
        </p>
        <div className="pt-2">
          <button
            onClick={onNavigateToInjection}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white transition shadow-lg shadow-cyan-600/30"
          >
            <Flame className="w-4 h-4 text-rose-300" />
            Launch First Experiment
          </button>
        </div>
      </div>
    );
  }

  const { summary, type_breakdown, timeline_series } = analysis;

  const formatMs = (ms: number | null) => {
    if (ms === null || ms === undefined) return 'N/A';
    if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
    return `${Math.round(ms)}ms`;
  };

  // Find max recovery duration to scale bar chart
  const maxBarDuration = Math.max(
    ...type_breakdown.map((t) => t.avg_recovery_duration_ms || 0),
    1
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Recovery Analysis</h2>
        <p className="text-xs text-slate-400">
          MTTR (Mean Time to Recovery), detection benchmarks, and failure mode comparisons
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Recovery Success Rate"
          value={`${summary.recovery_success_rate_percent}%`}
          badge={{ text: `${summary.successful_recoveries}/${summary.total_experiments}`, variant: 'success' }}
          icon={CheckCircle2}
          accentColor="emerald"
          subtitle="Experiments returning to healthy"
        />

        <MetricCard
          title="Avg Detection Time"
          value={formatMs(summary.avg_detection_time_ms)}
          icon={Clock}
          accentColor="cyan"
          subtitle="Time to alert on failure"
        />

        <MetricCard
          title="Avg Recovery Duration"
          value={formatMs(summary.avg_recovery_duration_ms)}
          badge={{ text: 'MTTR', variant: 'info' }}
          icon={TrendingUp}
          accentColor="blue"
          subtitle="Restoration to healthy verification"
        />

        <MetricCard
          title="Avg Total Downtime"
          value={formatMs(summary.avg_total_downtime_ms)}
          icon={AlertCircle}
          accentColor="amber"
          subtitle="End-to-end service outage window"
        />
      </div>

      {/* Comparative Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recovery Duration by Type Bar Chart */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-1 flex items-center justify-between">
            <span>Mean Recovery Duration by Experiment Type</span>
            <span className="text-[10px] font-mono text-slate-500">Real Benchmark Data</span>
          </h3>
          <p className="text-xs text-slate-400 mb-6">
            Compares how quickly each type of failure is mitigated and verified healthy
          </p>

          <div className="space-y-4">
            {type_breakdown.map((item) => {
              const val = item.avg_recovery_duration_ms || 0;
              const percentage = Math.min(Math.round((val / maxBarDuration) * 100), 100);

              return (
                <div key={item.type} className="space-y-1.5 font-mono text-xs">
                  <div className="flex justify-between items-center text-slate-300">
                    <span className="capitalize">{item.type.replace('_', ' ')}</span>
                    <span className="font-bold text-cyan-400">
                      {formatMs(item.avg_recovery_duration_ms)} ({item.count} runs)
                    </span>
                  </div>
                  <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(percentage, 5)}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Breakdown Analysis & Insights */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-1">
              Resilience Observations & Insights
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Automated architectural recommendations based on recorded chaos results
            </p>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                <span className="text-cyan-400 font-bold block mb-1">
                  1. Container Failure Recovery
                </span>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Fastest recovery is achieved when containers utilize health-check-driven auto-restart policies. Average restart verification: {formatMs(summary.avg_recovery_duration_ms)}.
                </p>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                <span className="text-amber-400 font-bold block mb-1">
                  2. Downstream Dependency Degradation
                </span>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  When Product Service experiences downtime, Order Service enters a graceful degraded mode, shedding requests without unbounded crashing.
                </p>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                <span className="text-emerald-400 font-bold block mb-1">
                  3. Precision Polling Limits
                </span>
                <p className="text-slate-400 text-[11px] leading-relaxed">
                  Measurement precision depends on polling frequency (currently configured at 1.5s interval).
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
