const UNEXPECTED_ERROR = 'Errore imprevisto, riprova.'

/** The message the API gave in `detail`, or a generic one. */
export function apiErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'detail' in error && typeof error.detail === 'string') {
    return error.detail
  }
  return UNEXPECTED_ERROR
}
