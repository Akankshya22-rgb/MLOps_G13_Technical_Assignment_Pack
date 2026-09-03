import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ModelService } from './model.service';
import { MlModel } from '../models/model';

describe('ModelService', () => {
  let service: ModelService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ModelService]
    });
    service = TestBed.inject(ModelService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('lists models without params when no search term is given', () => {
    service.list().subscribe();
    const req = httpMock.expectOne((r) => r.url === '/api/models');
    expect(req.request.method).toBe('GET');
    req.flush([]);
  });

  it('passes the search term as a query param', () => {
    service.list('pump').subscribe();
    const req = httpMock.expectOne((r) => r.url === '/api/models');
    expect(req.request.params.get('search')).toBe('pump');
    req.flush([]);
  });

  it('creates a model via POST', () => {
    const payload = { name: 'pump-failure-predictor', owner: 'Team', framework: 'sklearn' };
    const created: MlModel = { id: '1', ...payload, algorithm: null, description: null, tags: [], created_at: '', updated_at: '' };

    service.create(payload).subscribe((result) => expect(result).toEqual(created));

    const req = httpMock.expectOne('/api/models');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush(created);
  });

  it('approves a version via POST', () => {
    service.approveVersion('model-1', 'version-1').subscribe();
    const req = httpMock.expectOne('/api/models/model-1/versions/version-1/approve');
    expect(req.request.method).toBe('POST');
    req.flush({});
  });
});
