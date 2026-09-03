import { DestroyRef, signal } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { catchError, finalize, of, switchMap } from 'rxjs';

import { ApiError } from '../../core/models/api-error';

/**
 * Bridges an on-demand RxJS request (e.g. an HttpClient call) to template-friendly
 * signals, so every feature page gets the same loading / error / empty / success
 * states without repeating subscribe/catchError boilerplate.
 */
export class Resource<T> {
  readonly loading = signal(false);
  readonly error = signal<ApiError | null>(null);
  readonly data = signal<T | null>(null);

  private readonly trigger$ = new Subject<void>();
  private readonly latestSource = new BehaviorSubject<(() => Observable<T>) | null>(null);

  constructor(destroyRef: DestroyRef) {
    const sub = this.trigger$
      .pipe(
        switchMap(() => {
          const source = this.latestSource.value;
          if (!source) {
            return of(null);
          }
          this.loading.set(true);
          this.error.set(null);
          return source().pipe(
            catchError((err) => {
              this.error.set(err instanceof ApiError ? err : ApiError.fromHttpErrorResponse(err));
              return of(null);
            }),
            finalize(() => this.loading.set(false))
          );
        })
      )
      .subscribe((result) => {
        if (result !== null) {
          this.data.set(result);
        }
      });

    destroyRef.onDestroy(() => sub.unsubscribe());
  }

  /** (Re)loads the resource using the given source factory. */
  load(source: () => Observable<T>): void {
    this.latestSource.next(source);
    this.trigger$.next();
  }

  /** Re-runs the most recently used source, e.g. after a mutation or for a retry button. */
  reload(): void {
    this.trigger$.next();
  }
}
