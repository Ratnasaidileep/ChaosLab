export type ExperimentType =
  | 'container_failure'
  | 'cpu_stress'
  | 'memory_stress'
  | 'dependency_failure'
  | 'network_delay';

export type TargetService = 'product-service' | 'order-service';

export type ExperimentStatus =
  | 'PENDING'
  | 'INJECTING'
  | 'RUNNING'
  | 'DETECTED'
  | 'RECOVERING'
  | 'VERIFYING'
  | 'RECOVERED'
  | 'FAILED'
  | 'CANCELLED';

export interface ExperimentLog {
  timestamp: string;
  level: string;
  message: string;
}

export interface Experiment {
  id: string;
  type: ExperimentType;
  target_service: TargetService;
  parameters: {
    duration_seconds?: number;
    load_percent?: number;
    memory_mb?: number;
    delay_ms?: number;
    [key: string]: any;
  };
  status: ExperimentStatus;
  start_timestamp: string;
  failure_timestamp: string | null;
  detection_timestamp: string | null;
  recovery_start_timestamp: string | null;
  recovery_timestamp: string | null;
  detection_time_ms: number | null;
  recovery_duration_ms: number | null;
  total_downtime_ms: number | null;
  recovery_outcome: string | null;
  error_details: string | null;
  logs: ExperimentLog[];
}

export interface ServiceHealth {
  id: string;
  name: string;
  url: string;
  status: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY' | 'DOWN';
  http_status: number | null;
  latency_ms: number | null;
  last_checked: string;
  last_failure: string | null;
  last_recovery: string | null;
  details: Record<string, any>;
}

export interface DashboardSummary {
  overall_system_health: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  services: {
    'product-service': ServiceHealth;
    'order-service': ServiceHealth;
  };
  total_experiments: number;
  successful_recoveries: number;
  failed_recoveries: number;
  recovery_success_rate_percent: number;
  avg_recovery_duration_ms: number | null;
  avg_detection_time_ms: number | null;
  avg_total_downtime_ms: number | null;
  active_experiment: Experiment | null;
}

export interface RecoveryAnalysisData {
  summary: {
    total_experiments: number;
    successful_recoveries: number;
    failed_recoveries: number;
    recovery_success_rate_percent: number;
    avg_recovery_duration_ms: number | null;
    avg_detection_time_ms: number | null;
    avg_total_downtime_ms: number | null;
  };
  timeline_series: {
    id: string;
    type: string;
    target_service: string;
    start_time: string;
    detection_time_ms: number | null;
    recovery_duration_ms: number | null;
    total_downtime_ms: number | null;
  }[];
  type_breakdown: {
    type: string;
    count: number;
    avg_recovery_duration_ms: number | null;
    avg_total_downtime_ms: number | null;
  }[];
}
