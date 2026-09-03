import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideNoopAnimations } from '@angular/platform-browser/animations';

import { ModelListComponent } from './model-list.component';
import { MlModel } from '../../core/models/model';

describe('ModelListComponent', () => {
  let fixture: ComponentFixture<ModelListComponent>;
  let httpMock: HttpTestingController;

  const sampleModel: MlModel = {
    id: 'm1',
    name: 'pump-failure-predictor',
    owner: 'Reliability AI Team',
    framework: 'scikit-learn',
    algorithm: null,
    description: null,
    tags: ['industrial'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModelListComponent, HttpClientTestingModule],
      providers: [provideRouter([]), provideNoopAnimations()]
    }).compileComponents();

    fixture = TestBed.createComponent(ModelListComponent);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('shows a loading state before the models resolve', () => {
    fixture.detectChanges();
    expect(fixture.componentInstance.resource.loading()).toBeTrue();
    httpMock.expectOne((r) => r.url === '/api/models').flush([]);
  });

  it('renders models once loaded', () => {
    fixture.detectChanges();
    httpMock.expectOne((r) => r.url === '/api/models').flush([sampleModel]);
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('pump-failure-predictor');
    expect(text).toContain('Reliability AI Team');
  });

  it('shows an empty state when there are no models', () => {
    fixture.detectChanges();
    httpMock.expectOne((r) => r.url === '/api/models').flush([]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('No models match your search');
  });

  it('shows an error state when the request fails', () => {
    fixture.detectChanges();
    httpMock.expectOne((r) => r.url === '/api/models').flush(
      { error: { code: 'INTERNAL_ERROR', message: 'Something went wrong.', details: {} } },
      { status: 500, statusText: 'Server Error' }
    );
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Something went wrong.');
  });

  it('toggles the create-model form', () => {
    fixture.detectChanges();
    httpMock.expectOne((r) => r.url === '/api/models').flush([]);
    fixture.detectChanges();

    expect(fixture.componentInstance.showCreateForm()).toBeFalse();
    fixture.componentInstance.toggleCreateForm();
    expect(fixture.componentInstance.showCreateForm()).toBeTrue();
  });
});
