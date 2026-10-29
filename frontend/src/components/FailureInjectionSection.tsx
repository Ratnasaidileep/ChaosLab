import React, { useState } from 'react';
import {
  Flame,
  Cpu,
  Database,
  Unplug,
  WifiOff,
  Box,
  ShieldCheck,
  Play,
  Sliders,
  AlertTriangle
} from 'lucide-react';
import { ExperimentType, TargetService } from '../types';
import { FailureConfirmationModal } from './FailureConfirmationModal';

interface FailureInjectionSectionProps {
  onTriggerExperiment: (payload: {
    type: ExperimentType;
    target_service: TargetService;
    duration_seconds: number;
    load_percent?: number;
    memory_mb?: number;
    delay_ms?: number;
    confirm_destruction: boolean;
  }) => Promise<void>;
  isTriggering?: boolean;
}

export const FailureInjectionSection: React.FC<FailureInjectionSectionProps> = ({
  onTriggerExperiment,
  isTriggering = false,
}) => {
  // Modal state
  const [selectedExperiment, setSelectedExperiment] = useState<ExperimentType | null>(null);
  const [targetService, setTargetService] = useState<TargetService>('product-service');
  const [duration, setDuration] = useState<number>(15);
  const [cpuLoad, setCpuLoad] = useState<number>(70);
  const [memoryMb, setMemoryMb] = useState<number>(150);
  const [networkDelayMs, setNetworkDelayMs] = useState<number>(1000);

  const handleOpenModal = (type: ExperimentType, defaultTarget: TargetService) => {
    setSelectedExperiment(type);
    setTargetService(defaultTarget);
  };

  const handleConfirmInjection = async () => {
    if (!selectedExperiment) return;
    try {
      await onTriggerExperiment({
        type: selectedExperiment,
        target_service: targetService,
        duration_seconds: duration,
        load_percent: cpuLoad,
        memory_mb: memoryMb,
        delay_ms: networkDelayMs,
        confirm_destruction: true,
      });
      setSelectedExperiment(null);
    } catch {
      // Error is handled in App.tsx notification
    }
  };

  const experimentCards = [
    {
      type: 'container_failure' as ExperimentType,
      title: 'Container Failure',
      icon: Box,
      accent: 'rose',
      defaultService: 'product-service' as TargetService,
      allowedServices: ['product-service', 'order-service'] as TargetService[],
      description:
        'Stops or crashes the target test container. Evaluates Docker restart policy and automated health recovery.',
      impact: 'Immediate service unavailability until recovery controller verifies health.',
    },
    {
      type: 'cpu_stress' as ExperimentType,
      title: 'CPU Stress Workload',
      icon: Cpu,
      accent: 'amber',
      defaultService: 'product-service' as TargetService,
      allowedServices: ['product-service', 'order-service'] as TargetService[],
      description:
        'Spawns bounded worker threads consuming CPU up to safety limit (max 80%). Tests latency degradation under load.',
      impact: 'High CPU utilization and increased request latency.',
    },
    {
      type: 'memory_stress' as ExperimentType,
      title: 'Memory Stress Workload',
      icon: Database,
      accent: 'amber',
      defaultService: 'product-service' as TargetService,
      allowedServices: ['product-service', 'order-service'] as TargetService[],
      description:
        'Allocates a bounded block of memory (capped at 350 MB) inside the target service container to test memory pressure.',
      impact: 'Elevated RSS memory usage, automated cleanup on recovery.',
    },
    {
      type: 'dependency_failure' as ExperimentType,
      title: 'Service Dependency Failure',
      icon: Unplug,
      accent: 'rose',
      defaultService: 'order-service' as TargetService,
      allowedServices: ['order-service'] as TargetService[],
      description:
        'Simulates an outage or network partition of Product Service from the perspective of Order Service.',
      impact: 'Order Service reports degraded dependency health and fails order creation gracefully.',
    },
    {
      type: 'network_delay' as ExperimentType,
      title: 'Network Delay (Latency)',
      icon: WifiOff,
      accent: 'cyan',
      defaultService: 'product-service' as TargetService,
      allowedServices: ['product-service', 'order-service'] as TargetService[],
      description:
        'Injects artificial response latency (100ms - 3000ms) on API calls to test timeout thresholds and telemetry latency metrics.',
      impact: 'Artificial request delay observed on Prometheus latency histograms.',
    },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Controlled Failure Injection</h2>
        <p className="text-xs text-slate-400">
          Select and configure chaos resilience experiments with strict bounded limits
        </p>
      </div>

      {/* Safety Notice Banner */}
      <div className="bg-slate-900/90 border border-cyan-500/30 rounded-xl p-4 flex items-start gap-3 text-xs leading-relaxed">
        <ShieldCheck className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-slate-300">
          <span className="font-semibold text-white">DevOps Safety Isolation:</span> All experiments are restricted to designated project containers (allowlisted: <code className="text-cyan-400 font-mono">product-service</code>, <code className="text-cyan-400 font-mono">order-service</code>). Maximum duration is capped at 60s and resource consumption is bounded.
        </div>
      </div>

      {/* Experiment Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {experimentCards.map((exp) => {
          const Icon = exp.icon;
          return (
            <div
              key={exp.type}
              className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-2xl p-6 shadow-xl flex flex-col justify-between transition-all duration-200 group"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="p-3 rounded-xl bg-slate-800 text-cyan-400 border border-slate-700 group-hover:border-cyan-500/30 transition">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    Safe Bounded
                  </span>
                </div>

                <h3 className="mt-4 text-base font-bold text-white tracking-tight">
                  {exp.title}
                </h3>
                <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                  {exp.description}
                </p>

                <div className="mt-4 p-3 rounded-xl bg-slate-950/50 border border-slate-800/80 text-[11px] text-slate-300">
                  <span className="text-slate-500 block font-semibold mb-0.5">Observed Impact:</span>
                  {exp.impact}
                </div>
              </div>

              {/* Action */}
              <div className="mt-6 pt-4 border-t border-slate-800/80">
                <button
                  onClick={() => handleOpenModal(exp.type, exp.defaultService)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 text-xs font-bold rounded-xl bg-cyan-600/20 hover:bg-cyan-600 text-cyan-300 hover:text-white border border-cyan-500/30 transition-all shadow-sm"
                >
                  <Flame className="w-4 h-4 text-rose-400" />
                  Configure & Inject
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirmation & Parameter Modal */}
      {selectedExperiment && (
        <FailureConfirmationModal
          isOpen={true}
          onClose={() => setSelectedExperiment(null)}
          onConfirm={handleConfirmInjection}
          experimentType={selectedExperiment}
          targetService={targetService}
          setTargetService={setTargetService}
          parameters={{
            duration_seconds: duration,
            load_percent: cpuLoad,
            memory_mb: memoryMb,
            delay_ms: networkDelayMs,
          }}
          setParameters={{
            setDuration,
            setCpuLoad,
            setMemoryMb,
            setNetworkDelayMs,
          }}
          isLoading={isTriggering}
        />
      )}
    </div>
  );
};
