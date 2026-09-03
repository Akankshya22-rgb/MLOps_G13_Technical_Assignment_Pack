import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';

import { MetricService } from '../../core/services/metric.service';
import { ModelService } from '../../core/services/model.service';
import { ModelMetricsResponse } from '../../core/models/metric';
import { MlModel } from '../../core/models/model';
import { Resource } from '../../shared/utils/resource';
import { StatusChipComponent } from '../../shared/components/status-chip.component';
import { SparklineComponent } from '../../shared/components/sparkline.component';

@Component({
  selector: 'app-monitoring-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTableModule,
    StatusChipComponent,
    SparklineComponent
  ],
  templateUrl: './monitoring-dashboard.component.html',
  styleUrl: './monitoring-dashboard.component.css'
})
export class MonitoringDashboardComponent {
  private readonly metricService = inject(MetricService);
  private readonly modelService = inject(ModelService);
  private readonly fb = inject(FormBuilder);

  readonly models = signal<MlModel[]>([]);
  readonly resource = new Resource<ModelMetricsResponse>(inject(DestroyRef));
  readonly historyColumns = ['timestamp', 'version', 'environment', 'latency_ms', 'throughput_rpm', 'error_rate', 'quality_score', 'drift_score', 'availability'];

  readonly modelControl = this.fb.control<string | null>(null);

  latencyHistoryFor(version: string, environment: string): number[] {
    return (this.resource.data()?.history ?? [])
      .filter((m) => m.version === version && m.environment === environment)
      .map((m) => m.latency_ms);
  }

  constructor() {
    this.modelService.list().subscribe((models) => {
      this.models.set(models);
      if (models.length && !this.modelControl.value) {
        this.modelControl.setValue(models[0].id);
        this.reload();
      }
    });

    this.modelControl.valueChanges.subscribe(() => this.reload());
  }

  reload(): void {
    const modelId = this.modelControl.value;
    if (!modelId) return;
    this.resource.load(() => this.metricService.getModelMetrics(modelId));
  }
}
