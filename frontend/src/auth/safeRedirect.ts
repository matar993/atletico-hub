/**
 * The path to open after login: the `redirect` value when it is an internal path, Home otherwise. An internal path
 * starts with `/` and not with `//` or `/\`, which browsers read as another site.
 */
export function safeRedirect(redirect: string | undefined): string {
  if (redirect && redirect.startsWith('/') && !redirect.startsWith('//') && !redirect.startsWith('/\\')) {
    return redirect
  }
  return '/'
}
