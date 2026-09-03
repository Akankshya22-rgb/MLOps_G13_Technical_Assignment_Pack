import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { MlModel, MlModelWithVersions, ModelCreateRequest, ModelVersion, VersionCreateRequest } from '../models/model';

const BASE_URL = '/api/models';

@Injectable({ providedIn: 'root' })
export class ModelService {
  constructor(private readonly http: HttpClient) {}

  list(search?: string): Observable<MlModel[]> {
    const params: Record<string, string> = {};
    if (search) params['search'] = search;
    return this.http.get<MlModel[]>(BASE_URL, { params });
  }

  get(modelId: string): Observable<MlModelWithVersions> {
    return this.http.get<MlModelWithVersions>(`${BASE_URL}/${modelId}`);
  }

  create(payload: ModelCreateRequest): Observable<MlModel> {
    return this.http.post<MlModel>(BASE_URL, payload);
  }

  listVersions(modelId: string): Observable<ModelVersion[]> {
    return this.http.get<ModelVersion[]>(`${BASE_URL}/${modelId}/versions`);
  }

  createVersion(modelId: string, payload: VersionCreateRequest): Observable<ModelVersion> {
    return this.http.post<ModelVersion>(`${BASE_URL}/${modelId}/versions`, payload);
  }

  approveVersion(modelId: string, versionId: string): Observable<ModelVersion> {
    return this.http.post<ModelVersion>(`${BASE_URL}/${modelId}/versions/${versionId}/approve`, {});
  }
}
