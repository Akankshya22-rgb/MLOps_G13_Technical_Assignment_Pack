import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { DeploymentService } from './deployment.service';

describe('DeploymentService', () => {
  let service: DeploymentService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [DeploymentService]
    });
    service = TestBed.inject(DeploymentService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('applies filters as query params', () => {
    service.list({ model_id: 'm1', environment: 'production', status: 'FAILED' }).subscribe();
    const req = httpMock.expectOne((r) => r.url === '/api/deployments');
    expect(req.request.params.get('model_id')).toBe('m1');
    expect(req.request.params.get('environment')).toBe('production');
    expect(req.request.params.get('status')).toBe('FAILED');
    req.flush([]);
  });

  it('sends a retry request with simulate_failure flag', () => {
    service.retry('dep-1', true).subscribe();
    const req = httpMock.expectOne('/api/deployments/dep-1/retry');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ simulate_failure: true });
    req.flush({});
  });

  it('sends a rollback request', () => {
    service.rollback('dep-1').subscribe();
    const req = httpMock.expectOne('/api/deployments/dep-1/rollback');
    expect(req.request.method).toBe('POST');
    req.flush({});
  });
});
