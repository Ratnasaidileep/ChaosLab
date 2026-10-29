import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, X, Flame, Sliders } from 'lucide-react';
import { ExperimentType, TargetService } from '../types';

interface FailureConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  experimentType: ExperimentType;
  targetService: TargetService;
  setTargetService: (service: TargetService) => void;
  parameters: {
    duration_seconds: number;
    load_percent?: number;
    memory_mb?: number;
    delay_ms?: number;
  };
  setParameters: {
    setDuration: (val: number) => void;
    setCpuLoad: (val: number) => void;
    setMemoryMb: (val: number) => void;
    setNetworkDelayMs: (val: number) => void;
  };
  isLoading?: boolean;
}

export const FailureConfirmationModal: React.FC<FailureConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  experimentType,
  targetService,
  setTargetService,
  parameters,
  setParameters,
  isLoading = false,
}) => {
  const [confirmed, setConfirmed] = useState(false);

  if (!isOpen) return null;

  const formatTypeName = (t: ExperimentType) => {
    switch (t) {
      case 'container_failure':
        return 'Container Failure (Crash & Restart)';
      case 'cpu_stress':
        return 'CPU Stress Workload';
      case 'memory_stress':
        return 'Memory Pressure Workload';
      case 'dependency_failure':
        return 'Downstream Dependency Outage';
      case 'network_delay':
        return 'Network Latency Injection';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#0F172A] border border-rose-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              Confirm Controlled Failure Injection
            </h3>
            <p className="text-xs text-rose-400/90 font-mono">
              DevOps Resilience Experiment
            </p>
          </div>
        </div>

        {/* Notice Box */}
        <div className="mt-4 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25 flex gap-3 text-xs text-amber-200/90 leading-relaxed">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-300">Resilience Test Notice:</span> This action will intentionally perturb the designated service to observe automated detection and recovery time. No production or host system assets will be touched.
          </div>
        </div>

        {/* Experiment Configuration Details */}
        <div className="mt-4 bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3 font-mono text-xs">
          <div className="flex justify-between items-center border-b border-slate-800/80 pb-2">
            <span className="text-slate-400">Experiment Type:</span>
            <span className="text-cyan-400 font-semibold">{formatTypeName(experimentType)}</span>
          </div>

          {/* Target Service Selection */}
          <div className="flex justify-between items-center border-b border-slate-800/80 pb-2">
            <span className="text-slate-400">Target Microservice:</span>
            <select
              value={targetService}
              onChange={(e) => setTargetService(e.target.value as TargetService)}
              className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-white font-semibold focus:outline-none focus:border-cyan-500"
            >
              <option value="product-service">product-service</option>
              <option value="order-service">order-service</option>
            </select>
          </div>

          {/* Duration Slider */}
          <div className="space-y-1 border-b border-slate-800/80 pb-2">
            <div className="flex justify-between">
              <span className="text-slate-400">Auto-Recovery Duration:</span>
              <span className="text-amber-400 font-semibold">{parameters.duration_seconds}s</span>
            </div>
            <input
              type="range"
              min="5"
              max="60"
              step="5"
              value={parameters.duration_seconds}
              onChange={(e) => setParameters.setDuration(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {experimentType === 'cpu_stress' && (
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Target CPU Load:</span>
                <span className="text-cyan-400 font-semibold">{parameters.load_percent}% (Bounded)</span>
              </div>
              <input
                type="range"
                min="20"
                max="80"
                step="10"
                value={parameters.load_percent || 70}
                onChange={(e) => setParameters.setCpuLoad(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
            </div>
          )}

          {experimentType === 'memory_stress' && (
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Memory Allocation:</span>
                <span className="text-cyan-400 font-semibold">{parameters.memory_mb} MB (Capped)</span>
              </div>
              <input
                type="range"
                min="50"
                max="350"
                step="50"
                value={parameters.memory_mb || 150}
                onChange={(e) => setParameters.setMemoryMb(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
            </div>
          )}

          {experimentType === 'network_delay' && (
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Injected Delay:</span>
                <span className="text-cyan-400 font-semibold">{parameters.delay_ms} ms</span>
              </div>
              <input
                type="range"
                min="200"
                max="3000"
                step="200"
                value={parameters.delay_ms || 1000}
                onChange={(e) => setParameters.setNetworkDelayMs(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
            </div>
          )}
        </div>

        {/* Confirmation Checkbox */}
        <label className="mt-4 flex items-start gap-3 cursor-pointer group">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-1 h-4 w-4 rounded border-slate-700 bg-slate-900 text-rose-500 focus:ring-rose-500/30"
          />
          <span className="text-xs text-slate-300 group-hover:text-white transition">
            I confirm that this failure is intentionally injected for resilience testing and ChaosLab should measure detection and recovery telemetry.
          </span>
        </label>

        {/* Action Buttons */}
        <div className="mt-5 flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={!confirmed || isLoading}
            className={`flex items-center gap-2 px-5 py-2 text-xs font-bold rounded-lg transition shadow-lg ${
              confirmed && !isLoading
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-600/30 cursor-pointer'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            {isLoading ? 'Injecting...' : 'Inject Controlled Failure'}
          </button>
        </div>
      </div>
    </div>
  );
};
