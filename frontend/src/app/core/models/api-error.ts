import { HttpErrorResponse } from '@angular/common/http';

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}

export class ApiError extends Error {
  readonly code: string;
  readonly details: Record<string, unknown>;
  readonly status: number;

  constructor(status: number, body: Partial<ApiErrorBody> | null) {
    super(body?.error?.message ?? 'An unexpected error occurred. Please try again.');
    this.status = status;
    this.code = body?.error?.code ?? 'UNKNOWN_ERROR';
    this.details = body?.error?.details ?? {};
  }

  static fromHttpErrorResponse(err: HttpErrorResponse): ApiError {
    if (err.status === 0) {
      return new ApiError(0, {
        error: { code: 'NETWORK_ERROR', message: 'Could not reach the server. Check your connection and try again.', details: {} }
      });
    }
    if (err.error && typeof err.error === 'object' && 'error' in err.error) {
      return new ApiError(err.status, err.error as ApiErrorBody);
    }
    return new ApiError(err.status, {
      error: { code: 'UNKNOWN_ERROR', message: err.message || 'An unexpected error occurred.', details: {} }
    });
  }
}
