# ADR-0004: The web app ships as its own image and reaches the API on its own origin, under `/api`

**Date**: 2026-11-05
**Status**: accepted
**Deciders**: Marco Scalzo

## Context

The web app and the API run as separate processes. A browser that calls an API on another origin needs CORS rules and, for cookies, cross-site settings. The web app also needs a production server for its static build.

## Decision

The web app ships as its own image: its production build, served by unprivileged nginx, which forwards `/api/` to the API (`API_UPSTREAM`). The web app calls the API only under `/api` on its own origin. In development the Vite server proxies `/api` the same way. The API answers without the `/api` prefix.

## Alternatives Considered

### Alternative 1: The API serves the static build
- **Pros**: one image, one process
- **Cons**: web app and API releases are tied; static files go through Python
- **Why not**: separate images build, cache and scale apart, and nginx serves static files better

### Alternative 2: The web app calls the API on the API's origin, with CORS
- **Pros**: no proxy
- **Cons**: CORS rules and cross-site cookie settings to keep right in every environment
- **Why not**: one origin needs no CORS and keeps future session cookies first-party

## Consequences

### Positive
- No CORS configuration; cookies of a future login stay first-party
- The same `/api` path in development and in production

### Negative
- One more image to build and deploy

### Risks
- nginx and Vite proxy settings drift apart. Mitigation: browser tests run on the production build with the image's security headers
