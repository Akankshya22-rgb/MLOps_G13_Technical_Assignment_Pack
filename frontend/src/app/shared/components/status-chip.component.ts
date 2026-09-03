import { Component, Input } from '@angular/core';

const TONE_MAP: Record<string, 'neutral' | 'info' | 'success' | 'warn' | 'danger'> = {
  DRAFT: 'neutral',
  VALIDATED: 'info',
  APPROVED: 'info',
  STAGING: 'info',
  PRODUCTION: 'success',
  ARCHIVED: 'neutral',
  REQUESTED: 'neutral',
  VALIDATING: 'info',
  DEPLOYING: 'info',
  SUCCEEDED: 'success',
  FAILED: 'danger',
  ROLLED_BACK: 'warn',
  HEALTHY: 'success',
  DEGRADED: 'warn',
  UNHEALTHY: 'danger'
};

@Component({
  selector: 'app-status-chip',
  standalone: true,
  template: `<span class="status-chip" [class]="'tone-' + tone">{{ status }}</span>`,
  styles: [
    `
      .status-chip {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        white-space: nowrap;
      }
      .tone-neutral { background: #e0e0e0; color: #424242; }
      .tone-info { background: #e3f2fd; color: #0d47a1; }
      .tone-success { background: #e8f5e9; color: #1b5e20; }
      .tone-warn { background: #fff3e0; color: #e65100; }
      .tone-danger { background: #ffebee; color: #b71c1c; }
    `
  ]
})
export class StatusChipComponent {
  @Input({ required: true }) status!: string;

  get tone(): string {
    return TONE_MAP[this.status] ?? 'neutral';
  }
}
