import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { ModelService } from '../../core/services/model.service';
import { MlModel } from '../../core/models/model';
import { ApiError } from '../../core/models/api-error';
import { Resource } from '../../shared/utils/resource';

@Component({
  selector: 'app-model-list',
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
    MatTableModule
  ],
  templateUrl: './model-list.component.html',
  styleUrl: './model-list.component.css'
})
export class ModelListComponent {
  private readonly modelService = inject(ModelService);
  private readonly fb = inject(FormBuilder);
  private readonly snackBar = inject(MatSnackBar);

  readonly resource = new Resource<MlModel[]>(inject(DestroyRef));
  readonly columns = ['name', 'owner', 'framework', 'tags', 'created_at'];

  readonly searchControl = this.fb.control('');
  readonly showCreateForm = signal(false);
  readonly creating = signal(false);

  readonly createForm = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(200)]],
    owner: ['', [Validators.required, Validators.maxLength(200)]],
    framework: ['', [Validators.required, Validators.maxLength(100)]],
    algorithm: [''],
    description: [''],
    tags: ['']
  });

  constructor() {
    this.reload();
    this.searchControl.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed())
      .subscribe(() => this.reload());
  }

  reload(): void {
    const search = this.searchControl.value?.trim() || undefined;
    this.resource.load(() => this.modelService.list(search));
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
    this.modelService
      .create({
        name: raw.name,
        owner: raw.owner,
        framework: raw.framework,
        algorithm: raw.algorithm || undefined,
        description: raw.description || undefined,
        tags: raw.tags
          ? raw.tags
              .split(',')
              .map((t) => t.trim())
              .filter(Boolean)
          : []
      })
      .subscribe({
        next: () => {
          this.creating.set(false);
          this.showCreateForm.set(false);
          this.createForm.reset();
          this.snackBar.open('Model registered.', 'Dismiss', { duration: 3000 });
          this.reload();
        },
        error: (err) => {
          this.creating.set(false);
          this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 5000 });
        }
      });
  }
}
