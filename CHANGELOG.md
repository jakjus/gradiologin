# Changelog

## 0.2.0 — 2026-07-06

### Security
- **Removed the unauthenticated bypass for `{path}/api/predict` and `{path}/reset`.** Previously the Gradio API could be called without logging in; now every route requires a session unless explicitly listed in the new `public_paths` option.
- **No more hardcoded default `secret_key`.** If you don't pass one, a random key is generated at startup (with a warning). Previously the default was a publicly known string, making session cookies forgeable.
- OAuth error messages are now HTML-escaped before being rendered.

### Fixed
- `OAuthError` was referenced without being imported — any failed OAuth callback crashed with `NameError` instead of showing an error page.
- `mount_gradio_app` broke when called with keyword arguments (it read positional `args[2]`); it now has an explicit `(app, blocks, path, ...)` signature.
- With `no_login_page=True` and a single provider, `/login` now redirects straight to that provider instead of returning 404.
- Unknown provider names in `/login/{name}` and `/auth/{name}` return 404 instead of crashing.
- Root redirect to the login page now uses an absolute path.

### Added
- `public_paths` option on `mount_gradio_app`/`init` to exempt path prefixes (e.g. health checks) from authentication.
- `init` is now part of the public API for advanced setups.
- `__version__` attribute; package version is single-sourced from it.
- Type hints and docstrings throughout.
- Test suite (pytest) and GitHub Actions CI.
- Redesigned login page: valid HTML5, responsive, automatic dark mode.

### Removed
- Dead module `gradiologin/button.py` and unused duplicate `OAuth()` instance.
- Stale pinned `requirements.txt` (use `pip install -e .[dev]` for development).

## 0.1.0

- Initial release.
