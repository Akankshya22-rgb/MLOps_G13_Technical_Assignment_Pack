import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ModelMetricsResponse } from '../models/metric';

@Injectable({ providedIn: 'root' })
export class MetricService {
  constructor(private readonly http: HttpClient) {}

  getModelMetrics(modelId: string, version?: string, environment?: string): Observable<ModelMetricsResponse> {
    const params: Record<string, string> = {};
    if (version) params['version'] = version;
    if (environment) params['environment'] = environment;
    return this.http.get<ModelMetricsResponse>(`/api/models/${modelId}/metrics`, { params });
  }
}
