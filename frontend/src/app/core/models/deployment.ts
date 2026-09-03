export type DeploymentStatus = 'REQUESTED' | 'VALIDATING' | 'DEPLOYING' | 'SUCCEEDED' | 'FAILED' | 'ROLLED_BACK';

export interface DeploymentEvent {
  id: string;
  deployment_id: string;
  event_type: string;
  status: string;
  message: string | null;
  timestamp: string;
}

export interface Deployment {
  id: string;
  model_id: string;
  version_id: string;
  environment: string;
  status: DeploymentStatus;
  idempotency_key: string | null;
  attempt_count: number;
  error_message: string | null;
  requested_at: string;
  updated_at: string;
}

export interface DeploymentDetail extends Deployment {
  events: DeploymentEvent[];
}

export interface DeploymentCreateRequest {
  model_id: string;
  version_id: string;
  environment: string;
  idempotency_key?: string;
  simulate_failure?: boolean;
}
