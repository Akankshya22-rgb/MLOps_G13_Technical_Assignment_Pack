import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Deployment, DeploymentCreateRequest, DeploymentDetail } from '../models/deployment';

const BASE_URL = '/api/deployments';

export interface DeploymentFilters {
  model_id?: string;
  environment?: string;
  status?: string;
}

@Injectable({ providedIn: 'root' })
export class DeploymentService {
  constructor(private readonly http: HttpClient) {}

  list(filters: DeploymentFilters = {}): Observable<Deployment[]> {
    const params: Record<string, string> = {};
    if (filters.model_id) params['model_id'] = filters.model_id;
    if (filters.environment) params['environment'] = filters.environment;
    if (filters.status) params['status'] = filters.status;
    return this.http.get<Deployment[]>(BASE_URL, { params });
  }

  get(deploymentId: string): Observable<DeploymentDetail> {
    return this.http.get<DeploymentDetail>(`${BASE_URL}/${deploymentId}`);
  }

  create(payload: DeploymentCreateRequest): Observable<Deployment> {
    return this.http.post<Deployment>(BASE_URL, payload);
  }

  retry(deploymentId: string, simulateFailure = false): Observable<Deployment> {
    return this.http.post<Deployment>(`${BASE_URL}/${deploymentId}/retry`, { simulate_failure: simulateFailure });
  }

  rollback(deploymentId: string): Observable<Deployment> {
    return this.http.post<Deployment>(`${BASE_URL}/${deploymentId}/rollback`, {});
  }
}
