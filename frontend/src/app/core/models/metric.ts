export type MonitoringStatus = 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';

export interface Metric {
  id: string;
  model_id: string;
  version: string;
  environment: string;
  timestamp: string;
  latency_ms: number;
  throughput_rpm: number;
  error_rate: number;
  quality_score: number;
  drift_score: number;
  availability: number;
}

export interface MetricSummary {
  version: string;
  environment: string;
  latest: Metric | null;
  monitoring_status: MonitoringStatus;
  last_successful_inference: string | null;
  sample_count: number;
}

export interface ModelMetricsResponse {
  model_id: string;
  summaries: MetricSummary[];
  history: Metric[];
}
