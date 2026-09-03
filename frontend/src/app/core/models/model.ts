export type LifecycleStage = 'DRAFT' | 'VALIDATED' | 'APPROVED' | 'STAGING' | 'PRODUCTION' | 'ARCHIVED';

export interface ModelVersion {
  id: string;
  model_id: string;
  version: string;
  stage: LifecycleStage;
  approved: boolean;
  artifact_uri: string;
  training_data_ref: string | null;
  metadata: Record<string, unknown>;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface MlModel {
  id: string;
  name: string;
  owner: string;
  framework: string;
  algorithm: string | null;
  description: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface MlModelWithVersions extends MlModel {
  versions: ModelVersion[];
}

export interface ModelCreateRequest {
  name: string;
  owner: string;
  framework: string;
  algorithm?: string;
  description?: string;
  tags?: string[];
}

export interface VersionCreateRequest {
  version: string;
  artifact_uri: string;
  training_data_ref?: string;
  metadata?: Record<string, unknown>;
  notes?: string;
}
