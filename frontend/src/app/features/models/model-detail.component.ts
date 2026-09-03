import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ModelService } from '../../core/services/model.service';
import { MlModelWithVersions } from '../../core/models/model';
import { ApiError } from '../../core/models/api-error';
import { Resource } from '../../shared/utils/resource';
import { StatusChipComponent } from '../../shared/components/status-chip.component';

@Component({
  selector: 'app-model-detail',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatTooltipModule,
    StatusChipComponent
  ],
  templateUrl: './model-detail.component.html',
  styleUrl: './model-detail.component.css'
})
export class ModelDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly modelService = inject(ModelService);
  private readonly fb = inject(FormBuilder);
  private readonly snackBar = inject(MatSnackBar);

  readonly modelId = this.route.snapshot.paramMap.get('modelId')!;
  readonly resource = new Resource<MlModelWithVersions>(inject(DestroyRef));
  readonly versionColumns = ['version', 'stage', 'approved', 'artifact_uri', 'actions'];

  readonly showCreateForm = signal(false);
  readonly creating = signal(false);
  readonly approvingVersionId = signal<string | null>(null);

  readonly versionForm = this.fb.nonNullable.group({
    version: ['', [Validators.required, Validators.maxLength(50)]],
    artifact_uri: ['', [Validators.required, Validators.maxLength(500)]],
    training_data_ref: [''],
    notes: ['']
  });

  constructor() {
    this.reload();
  }

  reload(): void {
    this.resource.load(() => this.modelService.get(this.modelId));
  }

  toggleCreateForm(): void {
    this.showCreateForm.update((v) => !v);
  }

  submitVersion(): void {
    if (this.versionForm.invalid) {
      this.versionForm.markAllAsTouched();
      return;
    }
    const raw = this.versionForm.getRawValue();
    this.creating.set(true);
    this.modelService
      .createVersion(this.modelId, {
        version: raw.version,
        artifact_uri: raw.artifact_uri,
        training_data_ref: raw.training_data_ref || undefined,
        notes: raw.notes || undefined
      })
      .subscribe({
        next: () => {
          this.creating.set(false);
          this.showCreateForm.set(false);
          this.versionForm.reset();
          this.snackBar.open('Version registered.', 'Dismiss', { duration: 3000 });
          this.reload();
        },
        error: (err) => {
          this.creating.set(false);
          this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 5000 });
        }
      });
  }

  approve(versionId: string): void {
    this.approvingVersionId.set(versionId);
    this.modelService.approveVersion(this.modelId, versionId).subscribe({
      next: () => {
        this.approvingVersionId.set(null);
        this.snackBar.open('Version approved.', 'Dismiss', { duration: 3000 });
        this.reload();
      },
      error: (err) => {
        this.approvingVersionId.set(null);
        this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 5000 });
      }
    });
  }

  deploy(versionId: string): void {
    this.router.navigate(['/deployments'], { queryParams: { modelId: this.modelId, versionId } });
  }
}
