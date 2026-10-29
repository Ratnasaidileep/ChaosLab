import React from 'react';
import { X, Clock, CheckCircle2, XCircle, AlertTriangle, Terminal, Info, ShieldCheck } from 'lucide-react';
import { Experiment } from '../types';

interface ExperimentDetailModalProps {
  experiment: Experiment | null;
  onClose: () => void;
}

export const ExperimentDetailModal: React.FC<ExperimentDetailModalProps> = ({
  experiment,
  onClose,
}) => {
  if (!experiment) return null;

  const formatMs = (ms: number | null) => {
    if (ms === null || ms === undefined) return 'N/A';
    if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s (${Math.round(ms)}ms)`;
    return `${Math.round(ms)}ms`;
  };

  const getStatusBadge = (status: string, outcome: string | null) => {
    if (status === 'RECOVERED' || outcome === 'SUCCESS') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-3.5 h-3.5" />
          VERIFIED RECOVERED
        </span>
      );
    }
    if (status === 'CANCELLED') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          CANCELLED
        </span>
      );
    }
    if (status === 'FAILED') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30">
          <XCircle className="w-3.5 h-3.5" />
          FAILED RECOVERY
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3.5 h-3.5" />
        {status}
      </span>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#0F172A] border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[90vh] flex flex-col">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white font-mono">
                {experiment.id}
              </h3>
              {getStatusBadge(experiment.status, experiment.recovery_outcome)}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Type: <span className="text-cyan-400 font-mono font-medium">{experiment.type}</span> &bull; Target: <span className="text-white font-mono">{experiment.target_service}</span>
            </p>
          </div>
        </div>

        {/* Content Body */}
        <div className="overflow-y-auto space-y-5 py-4 pr-1">
          {/* Recovery Math & Timestamps Breakdown */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-cyan-400" />
              Calculated Telemetry Metrics
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
                <span className="text-slate-400 block text-[11px]">Detection Time:</span>
                <span className="text-sm font-bold text-cyan-400">
                  {formatMs(experiment.detection_time_ms)}
                </span>
                <span className="block text-[10px] text-slate-500 mt-1">Detection - Failure</span>
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
                <span className="text-slate-400 block text-[11px]">Recovery Duration:</span>
                <span className="text-sm font-bold text-emerald-400">
                  {formatMs(experiment.recovery_duration_ms)}
                </span>
                <span className="block text-[10px] text-slate-500 mt-1">Verified - Recov Start</span>
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
                <span className="text-slate-400 block text-[11px]">Total Downtime:</span>
                <span className="text-sm font-bold text-amber-400">
                  {formatMs(experiment.total_downtime_ms)}
                </span>
                <span className="block text-[10px] text-slate-500 mt-1">Verified - Failure Start</span>
              </div>
            </div>
          </div>

          {/* Timestamps Trace Table */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              Lifecycle Timestamp Trace
            </h4>
            <div className="space-y-1.5 font-mono text-xs">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Experiment Registered:</span>
                <span className="text-slate-200">{experiment.start_timestamp}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Failure Injected:</span>
                <span className="text-rose-400">{experiment.failure_timestamp || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Failure Detected:</span>
                <span className="text-cyan-400">{experiment.detection_timestamp || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Recovery Triggered:</span>
                <span className="text-amber-400">{experiment.recovery_start_timestamp || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Verified Healthy Again:</span>
                <span className="text-emerald-400">{experiment.recovery_timestamp || 'Unverified'}</span>
              </div>
            </div>
          </div>

          {/* Parameters & Error Details */}
          {experiment.error_details && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-mono">
              <span className="font-bold text-rose-200 block mb-1">Diagnostic Error Details:</span>
              {experiment.error_details}
            </div>
          )}

          {/* Execution Logs */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-cyan-400" />
              Experiment Execution Logs
            </h4>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-xs space-y-1.5 max-h-48 overflow-y-auto">
              {experiment.logs && experiment.logs.length > 0 ? (
                experiment.logs.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-slate-300">
                    <span className="text-slate-500 text-[10px] shrink-0">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-1 rounded uppercase shrink-0 ${
                        log.level === 'ERROR'
                          ? 'bg-rose-500/20 text-rose-400'
                          : log.level === 'WARNING'
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-cyan-500/10 text-cyan-400'
                      }`}
                    >
                      {log.level}
                    </span>
                    <span className="text-slate-300 break-words">{log.message}</span>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 text-center py-2">No logs recorded.</div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
