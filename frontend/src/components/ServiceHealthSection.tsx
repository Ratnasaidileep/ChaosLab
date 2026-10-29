import React, { useState } from 'react';
import {
  Server,
  ShoppingCart,
  RefreshCw,
  Clock,
  Cpu,
  Database,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ExternalLink
} from 'lucide-react';
import { ServiceHealth } from '../types';

interface ServiceHealthSectionProps {
  services: ServiceHealth[];
  onVerifyService: (serviceId: string) => Promise<void>;
}

export const ServiceHealthSection: React.FC<ServiceHealthSectionProps> = ({
  services,
  onVerifyService,
}) => {
  const [verifyingId, setVerifyingId] = useState<string | null>(null);

  const handleVerify = async (id: string) => {
    setVerifyingId(id);
    try {
      await onVerifyService(id);
    } finally {
      setVerifyingId(null);
    }
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'HEALTHY':
        return {
          icon: CheckCircle,
          text: 'HEALTHY',
          color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
          dot: 'bg-emerald-400',
        };
      case 'DEGRADED':
        return {
          icon: AlertTriangle,
          text: 'DEGRADED',
          color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
          dot: 'bg-amber-400',
        };
      default:
        return {
          icon: XCircle,
          text: 'DOWN / UNHEALTHY',
          color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
          dot: 'bg-rose-400',
        };
    }
  };

  const formatTimestamp = (ts: string | null) => {
    if (!ts) return 'Never recorded';
    try {
      return new Date(ts).toLocaleTimeString() + ' (' + new Date(ts).toLocaleDateString() + ')';
    } catch {
      return ts;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Service Health Status</h2>
        <p className="text-xs text-slate-400">
          Continuous active health probes and downstream dependency monitoring
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {services.map((svc) => {
          const statusInfo = getStatusDisplay(svc.status);
          const StatusIcon = statusInfo.icon;
          const isVerifying = verifyingId === svc.id;

          return (
            <div
              key={svc.id}
              className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden flex flex-col justify-between"
            >
              {/* Header */}
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-slate-800 border border-slate-700 text-cyan-400">
                      {svc.id === 'product-service' ? (
                        <Server className="w-6 h-6" />
                      ) : (
                        <ShoppingCart className="w-6 h-6" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        {svc.name}
                        <span className="text-[10px] font-mono font-normal text-slate-400 px-2 py-0.5 rounded bg-slate-800">
                          {svc.id}
                        </span>
                      </h3>
                      <a
                        href={svc.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs font-mono text-cyan-400/80 hover:text-cyan-300 flex items-center gap-1 transition"
                      >
                        {svc.url}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <span
                    className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${statusInfo.color}`}
                  >
                    <span className={`w-2 h-2 rounded-full ${statusInfo.dot} animate-pulse`}></span>
                    {statusInfo.text}
                  </span>
                </div>

                {/* Metrics & Details Grid */}
                <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 gap-3 font-mono text-xs">
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                    <span className="text-slate-400 block text-[11px]">HTTP Status</span>
                    <span className="font-bold text-white text-sm">
                      {svc.http_status || 'Connection Refused'}
                    </span>
                  </div>

                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                    <span className="text-slate-400 block text-[11px]">Probe Latency</span>
                    <span className="font-bold text-cyan-400 text-sm">
                      {svc.latency_ms !== null ? `${svc.latency_ms} ms` : 'N/A'}
                    </span>
                  </div>

                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                    <span className="text-slate-400 block text-[11px]">Last Checked</span>
                    <span className="font-medium text-slate-300 truncate block text-xs">
                      {new Date(svc.last_checked).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                {/* Downstream Dependencies & Internal Health */}
                <div className="mt-4 p-4 rounded-xl bg-slate-950/40 border border-slate-800 space-y-2 text-xs">
                  <span className="font-semibold text-slate-300 block">Telemetry & Dependencies</span>
                  <div className="space-y-1 text-slate-400 font-mono text-[11px]">
                    {svc.id === 'order-service' && (
                      <div className="flex justify-between py-1 border-b border-slate-800/60">
                        <span>Dependency: product-service</span>
                        <span
                          className={
                            svc.details?.dependencies?.product_service === 'ok'
                              ? 'text-emerald-400'
                              : 'text-rose-400 font-bold'
                          }
                        >
                          {svc.details?.dependencies?.product_service || 'Unknown'}
                        </span>
                      </div>
                    )}

                    <div className="flex justify-between py-1 border-b border-slate-800/60">
                      <span>Last Injected Failure:</span>
                      <span className="text-rose-400/90">{formatTimestamp(svc.last_failure)}</span>
                    </div>

                    <div className="flex justify-between py-1">
                      <span>Last Verified Recovery:</span>
                      <span className="text-emerald-400/90">{formatTimestamp(svc.last_recovery)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center">
                <span className="text-[11px] text-slate-500 font-mono">
                  Auto-polled every 1.5s
                </span>
                <button
                  onClick={() => handleVerify(svc.id)}
                  disabled={isVerifying}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition border border-slate-700 shadow-sm"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? 'animate-spin text-cyan-400' : ''}`} />
                  {isVerifying ? 'Verifying...' : 'Verify Health Now'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
