import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';

import { DeploymentService } from '../../core/services/deployment.service';
import { ModelService } from '../../core/services/model.service';
import { Deployment } from '../../core/models/deployment';
import { MlModel, ModelVersion } from '../../core/models/model';
import { ApiError } from '../../core/models/api-error';
import { Resource } from '../../shared/utils/resource';
import { StatusChipComponent } from '../../shared/components/status-chip.component';

@Component({
  selector: 'app-deployment-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTableModule,
    StatusChipComponent
  ],
  templateUrl: './deployment-list.component.html',
  styleUrl: './deployment-list.component.css'
})
export class DeploymentListComponent {
  private readonly deploymentService = inject(DeploymentService);
  private readonly modelService = inject(ModelService);
  private readonly fb = inject(FormBuilder);
  private readonly snackBar = inject(MatSnackBar);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly resource = new Resource<Deployment[]>(inject(DestroyRef));
  readonly columns = ['environment', 'model_id', 'version_id', 'status', 'attempt_count', 'requested_at', 'actions'];

  readonly models = signal<MlModel[]>([]);
  readonly versionsByModel = signal<ModelVersion[]>([]);
  readonly showCreateForm = signal(false);
  readonly creating = signal(false);
  readonly actingDeploymentId = signal<string | null>(null);

  readonly filterForm = this.fb.nonNullable.group({
    model_id: [''],
    environment: [''],
    status: ['']
  });

  readonly createForm = this.fb.nonNullable.group({
    model_id: ['', Validators.required],
    version_id: ['', Validators.required],
    environment: ['staging', Validators.required],
    idempotency_key: [''],
    simulate_failure: [false]
  });

  constructor() {
    this.modelService.list().subscribe((models) => this.models.set(models));
    this.reload();

    const queryModelId = this.route.snapshot.queryParamMap.get('modelId');
    const queryVersionId = this.route.snapshot.queryParamMap.get('versionId');
    if (queryModelId) {
      this.showCreateForm.set(true);
      this.createForm.patchValue({ model_id: queryModelId, environment: 'production' });
      this.onModelChange(queryModelId, queryVersionId ?? undefined);
    }
  }

  reload(): void {
    const raw = this.filterForm.getRawValue();
    this.resource.load(() =>
      this.deploymentService.list({
        model_id: raw.model_id || undefined,
        environment: raw.environment || undefined,
        status: raw.status || undefined
      })
    );
  }

  onModelChange(modelId: string, preselectVersionId?: string): void {
    this.createForm.patchValue({ version_id: '' });
    if (!modelId) {
      this.versionsByModel.set([]);
      return;
    }
    this.modelService.listVersions(modelId).subscribe((versions) => {
      this.versionsByModel.set(versions);
      if (preselectVersionId) {
        this.createForm.patchValue({ version_id: preselectVersionId });
      }
    });
  }

  toggleCreateForm(): void {
    this.showCreateForm.update((v) => !v);
  }

  submitCreate(): void {
    if (this.createForm.invalid) {
      this.createForm.markAllAsTouched();
      return;
    }
    const raw = this.createForm.getRawValue();
    this.creating.set(true);
    this.deploymentService
      .create({
        model_id: raw.model_id,
        version_id: raw.version_id,
        environment: raw.environment,
        idempotency_key: raw.idempotency_key || undefined,
        simulate_failure: raw.simulate_failure
      })
      .subscribe({
        next: (deployment) => {
          this.creating.set(false);
          this.showCreateForm.set(false);
          this.createForm.reset({ environment: 'staging', simulate_failure: false });
          this.router.navigate([], { queryParams: {} });
          const message = deployment.status === 'SUCCEEDED' ? 'Deployment succeeded.' : `Deployment ended as ${deployment.status}.`;
          this.snackBar.open(message, 'Dismiss', { duration: 4000 });
          this.reload();
        },
        error: (err) => {
          this.creating.set(false);
          this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 6000 });
        }
      });
  }

  retry(deploymentId: string): void {
    this.actingDeploymentId.set(deploymentId);
    this.deploymentService.retry(deploymentId).subscribe({
      next: (deployment) => {
        this.actingDeploymentId.set(null);
        this.snackBar.open(`Retry ended as ${deployment.status}.`, 'Dismiss', { duration: 4000 });
        this.reload();
      },
      error: (err) => {
        this.actingDeploymentId.set(null);
        this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 6000 });
      }
    });
  }

  rollback(deploymentId: string): void {
    this.actingDeploymentId.set(deploymentId);
    this.deploymentService.rollback(deploymentId).subscribe({
      next: () => {
        this.actingDeploymentId.set(null);
        this.snackBar.open('Deployment rolled back.', 'Dismiss', { duration: 4000 });
        this.reload();
      },
      error: (err) => {
        this.actingDeploymentId.set(null);
        this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 6000 });
      }
    });
  }

  modelName(modelId: string): string {
    return this.models().find((m) => m.id === modelId)?.name ?? modelId;
  }
}
