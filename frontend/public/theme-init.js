// Runs in <head> before the CSS, so the first paint already has the right theme.
// It is a file, not inline code, because the Content-Security-Policy forbids inline scripts.
// Keep the storage key and the values in sync with src/theme/.
;(function () {
  var choice = 'system'
  try {
    var saved = localStorage.getItem('theme')
    if (saved === 'light' || saved === 'dark') choice = saved
  } catch {
    // Storage blocked: fall back to the system theme.
  }
  var dark = choice === 'dark' || (choice === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', dark)
})()
