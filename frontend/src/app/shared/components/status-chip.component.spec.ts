import { TestBed } from '@angular/core/testing';

import { StatusChipComponent } from './status-chip.component';

describe('StatusChipComponent', () => {
  it('renders the status text', () => {
    TestBed.configureTestingModule({ imports: [StatusChipComponent] });
    const fixture = TestBed.createComponent(StatusChipComponent);
    fixture.componentInstance.status = 'PRODUCTION';
    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement;
    expect(el.textContent?.trim()).toBe('PRODUCTION');
  });

  it('applies a success tone for healthy/production/succeeded states', () => {
    TestBed.configureTestingModule({ imports: [StatusChipComponent] });
    const fixture = TestBed.createComponent(StatusChipComponent);
    fixture.componentInstance.status = 'SUCCEEDED';
    fixture.detectChanges();

    const chip = fixture.nativeElement.querySelector('.status-chip');
    expect(chip.classList).toContain('tone-success');
  });

  it('applies a danger tone for failed/unhealthy states', () => {
    TestBed.configureTestingModule({ imports: [StatusChipComponent] });
    const fixture = TestBed.createComponent(StatusChipComponent);
    fixture.componentInstance.status = 'FAILED';
    fixture.detectChanges();

    const chip = fixture.nativeElement.querySelector('.status-chip');
    expect(chip.classList).toContain('tone-danger');
  });

  it('falls back to a neutral tone for unknown statuses', () => {
    TestBed.configureTestingModule({ imports: [StatusChipComponent] });
    const fixture = TestBed.createComponent(StatusChipComponent);
    fixture.componentInstance.status = 'SOMETHING_UNKNOWN';
    fixture.detectChanges();

    const chip = fixture.nativeElement.querySelector('.status-chip');
    expect(chip.classList).toContain('tone-neutral');
  });
});
