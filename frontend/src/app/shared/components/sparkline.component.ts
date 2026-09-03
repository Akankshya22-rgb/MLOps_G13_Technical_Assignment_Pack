import { Component, Input, computed, signal } from '@angular/core';

@Component({
  selector: 'app-sparkline',
  standalone: true,
  template: `
    <svg [attr.viewBox]="'0 0 ' + width + ' ' + height" preserveAspectRatio="none" class="sparkline">
      <polyline [attr.points]="points()" fill="none" [attr.stroke]="color" stroke-width="2" />
    </svg>
  `,
  styles: [
    `
      .sparkline {
        width: 100%;
        height: 40px;
        display: block;
      }
    `
  ]
})
export class SparklineComponent {
  private readonly widthPx = 120;
  private readonly heightPx = 40;

  readonly width = this.widthPx;
  readonly height = this.heightPx;

  private readonly valuesSignal = signal<number[]>([]);
  @Input() color = '#1565c0';

  @Input() set values(v: number[]) {
    this.valuesSignal.set(v ?? []);
  }

  readonly points = computed(() => {
    const values = this.valuesSignal();
    if (!values.length) return '';
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const step = values.length > 1 ? this.widthPx / (values.length - 1) : 0;

    return values
      .map((value, index) => {
        const x = index * step;
        const y = this.heightPx - ((value - min) / range) * this.heightPx;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  });
}
