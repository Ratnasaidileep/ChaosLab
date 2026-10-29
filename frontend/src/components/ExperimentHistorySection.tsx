import React, { useState } from 'react';
import {
  History,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Eye,
  RefreshCw,
  Ban
} from 'lucide-react';
import { Experiment, ExperimentType, TargetService } from '../types';
import { ExperimentDetailModal } from './ExperimentDetailModal';

interface ExperimentHistorySectionProps {
  experiments: Experiment[];
  onRefresh: () => void;
  isLoading?: boolean;
}

export const ExperimentHistorySection: React.FC<ExperimentHistorySectionProps> = ({
  experiments,
  onRefresh,
  isLoading = false,
}) => {
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedService, setSelectedService] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [activeModalExp, setActiveModalExp] = useState<Experiment | null>(null);

  const filteredExperiments = experiments.filter((exp) => {
    const matchesSearch =
      exp.id.toLowerCase().includes(search.toLowerCase()) ||
      exp.type.toLowerCase().includes(search.toLowerCase()) ||
      exp.target_service.toLowerCase().includes(search.toLowerCase());

    const matchesType = selectedType === 'ALL' || exp.type === selectedType;
    const matchesService =
      selectedService === 'ALL' || exp.target_service === selectedService;
    const matchesStatus = selectedStatus === 'ALL' || exp.status === selectedStatus;

    return matchesSearch && matchesType && matchesService && matchesStatus;
  });

  const formatMs = (ms: number | null) => {
    if (ms === null || ms === undefined) return '-';
    if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
    return `${Math.round(ms)}ms`;
  };

  const getStatusBadge = (status: string, outcome: string | null) => {
    if (status === 'RECOVERED' || outcome === 'SUCCESS') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3" />
          Recovered
        </span>
      );
    }
    if (status === 'CANCELLED') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-slate-800 text-slate-400 border border-slate-700">
          <Ban className="w-3 h-3" />
          Cancelled
        </span>
      );
    }
    if (status === 'FAILED') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30">
          <XCircle className="w-3 h-3" />
          Failed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3 h-3" />
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Experiment History</h2>
          <p className="text-xs text-slate-400">
            Recorded audit logs, calculated downtime metrics, and verified recovery outcomes
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          Refresh History
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between shadow-lg">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search experiments by ID, type, or service..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition font-mono"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 transition font-mono"
          >
            <option value="ALL">All Types</option>
            <option value="container_failure">Container Failure</option>
            <option value="cpu_stress">CPU Stress</option>
            <option value="memory_stress">Memory Stress</option>
            <option value="dependency_failure">Dependency Failure</option>
            <option value="network_delay">Network Delay</option>
          </select>

          {/* Service Filter */}
          <select
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 transition font-mono"
          >
            <option value="ALL">All Services</option>
            <option value="product-service">Product Service</option>
            <option value="order-service">Order Service</option>
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500 transition font-mono"
          >
            <option value="ALL">All Statuses</option>
            <option value="RECOVERED">Recovered</option>
            <option value="FAILED">Failed</option>
            <option value="CANCELLED">Cancelled</option>
            <option value="RUNNING">Running</option>
          </select>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono uppercase text-[11px]">
              <tr>
                <th className="px-4 py-3">Experiment ID</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Target</th>
                <th className="px-4 py-3">Injected At</th>
                <th className="px-4 py-3">Detection</th>
                <th className="px-4 py-3">Recovery Duration</th>
                <th className="px-4 py-3">Total Downtime</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredExperiments.length > 0 ? (
                filteredExperiments.map((exp) => (
                  <tr
                    key={exp.id}
                    className="hover:bg-slate-800/40 transition cursor-pointer"
                    onClick={() => setActiveModalExp(exp)}
                  >
                    <td className="px-4 py-3 font-semibold text-cyan-400 whitespace-nowrap">
                      {exp.id}
                    </td>
                    <td className="px-4 py-3 text-slate-200 whitespace-nowrap">
                      {exp.type.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">
                      {exp.target_service}
                    </td>
                    <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                      {new Date(exp.start_timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-3 text-cyan-400/90 whitespace-nowrap">
                      {formatMs(exp.detection_time_ms)}
                    </td>
                    <td className="px-4 py-3 text-emerald-400 font-semibold whitespace-nowrap">
                      {formatMs(exp.recovery_duration_ms)}
                    </td>
                    <td className="px-4 py-3 text-amber-400 font-semibold whitespace-nowrap">
                      {formatMs(exp.total_downtime_ms)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {getStatusBadge(exp.status, exp.recovery_outcome)}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveModalExp(exp);
                        }}
                        className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition"
                        title="View Full Telemetry Trace"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="px-4 py-8 text-center text-slate-500 font-sans">
                    No chaos experiments recorded matching current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {activeModalExp && (
        <ExperimentDetailModal
          experiment={activeModalExp}
          onClose={() => setActiveModalExp(null)}
        />
      )}
    </div>
  );
};
