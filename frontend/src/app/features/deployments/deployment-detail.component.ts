import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { DeploymentService } from '../../core/services/deployment.service';
import { DeploymentDetail } from '../../core/models/deployment';
import { ApiError } from '../../core/models/api-error';
import { Resource } from '../../shared/utils/resource';
import { StatusChipComponent } from '../../shared/components/status-chip.component';

@Component({
  selector: 'app-deployment-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule, MatIconModule, MatProgressSpinnerModule, StatusChipComponent],
  templateUrl: './deployment-detail.component.html',
  styleUrl: './deployment-detail.component.css'
})
export class DeploymentDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly deploymentService = inject(DeploymentService);
  private readonly snackBar = inject(MatSnackBar);

  readonly deploymentId = this.route.snapshot.paramMap.get('deploymentId')!;
  readonly resource = new Resource<DeploymentDetail>(inject(DestroyRef));
  readonly acting = signal(false);

  constructor() {
    this.reload();
  }

  reload(): void {
    this.resource.load(() => this.deploymentService.get(this.deploymentId));
  }

  retry(): void {
    this.acting.set(true);
    this.deploymentService.retry(this.deploymentId).subscribe({
      next: (deployment) => {
        this.acting.set(false);
        this.snackBar.open(`Retry ended as ${deployment.status}.`, 'Dismiss', { duration: 4000 });
        this.reload();
      },
      error: (err) => {
        this.acting.set(false);
        this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 6000 });
      }
    });
  }

  rollback(): void {
    this.acting.set(true);
    this.deploymentService.rollback(this.deploymentId).subscribe({
      next: () => {
        this.acting.set(false);
        this.snackBar.open('Deployment rolled back.', 'Dismiss', { duration: 4000 });
        this.reload();
      },
      error: (err) => {
        this.acting.set(false);
        this.snackBar.open(ApiError.fromHttpErrorResponse(err).message, 'Dismiss', { duration: 6000 });
      }
    });
  }
}
