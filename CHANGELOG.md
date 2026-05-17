# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-05-17

### Added

- **TOML config file** support — `~/.config/coverart-cli/config.toml`,
  `./coverart.toml`, or `--config PATH`. CLI flags still override the config.
- **`py.typed`** marker file for PEP 561 — type checkers can now see our types.
- **Public library API** explicitly defined via `__all__` in
  `coverart_cli/__init__.py`. You can now do
  `from coverart_cli import RunOptions, run, ITunesProvider`.
- **`.editorconfig`** for cross-IDE consistency.
- **`.pre-commit-config.yaml`** with ruff + ruff-format + standard checks.
- **`SECURITY.md`** with private vulnerability reporting link.
- **PyPI release workflow** (`.github/workflows/release.yml`) — push a
  `v*` tag and the package is built and uploaded via PyPI Trusted Publishing.
  Includes a **`needs: test`** gate so a red main can't ship a release.
- **Dependabot** monthly checks for GitHub Actions and pip.

### Changed

- Minimum Python is now **3.11** (was 3.10) — needed for stdlib `tomllib`.
- Metadata now uses **PEP 639 SPDX** (`license = "MIT"` + `license-files`),
  no more deprecated `License ::` classifier.
- Description and CLI help text now reflect the actual provider and format
  coverage (4 providers, 5 formats).
- All providers share a single `_default_user_agent()` derived from
  `__version__` — no more stale `0.1.0` strings hard-coded in defaults.
- `iTunesProvider` and `DeezerProvider` correctly accept `user_agent=`
  (was silently ignored, broke library usage).
- `MusicBrainzProvider` dead `release` fallback branch removed.
- Size threshold for accepted covers unified across providers via
  `tagging.MIN_COVER_BYTES`.
- `scan_library` path-traversal logic simplified to `relative_to` +
  `ValueError` guard.

## [0.2.0] - 2026-05-17

### Added

- **iTunes provider** (Apple Music public search) — no API key required.
- **Deezer provider** — no API key required.
- **FLAC, Ogg Vorbis, and Opus** file format support (read + embed).
- HTML report shows iTunes / Deezer / Embedded filter chips and badges.
- Demo report generator (`docs/make_demo_report.py`).
- **`--min-bytes N`**: upgrade existing covers smaller than N bytes. Default 0
  (keep all existing). Setting e.g. `--min-bytes 50000` causes the tool to
  re-fetch covers for any album whose current artwork is below 50 KB.
- **`--replace-smaller`**: when the freshly fetched cover is larger than the
  existing one, replace it. Default is to keep the larger existing cover when
  both qualify.
- `existing_embedded_size()` helper in `coverart_cli.tagging` for inspecting
  in-tag artwork sizes across all five formats.

### Changed

- Last.fm is now optional — if no key is supplied, the tool runs with the three
  free providers instead of failing.
- README rewritten — significantly shorter, with screenshots and an
  alternatives table.

## [0.1.0] - 2026-05-17

### Added

- Initial release.
- Tag-first album metadata reading via `mutagen`, directory-name fallback.
- Last.fm `album.getinfo` provider with placeholder-image rejection.
- MusicBrainz + Cover Art Archive fallback provider with rate limiting.
- Embed into MP3 (`ID3 APIC`) and M4A (`covr` atom).
- Sidecar `cover.jpg` / `cover.png` writing with magic-byte MIME detection.
- CLI: `--lastfm-key`, `--no-lastfm`, `--no-musicbrainz`, `--no-embed`,
  `--no-sidecar`, `--dry-run`, `--missing-csv`, `-v`/`-vv`.
- **HTML coverage report**: `--report-html PATH`, `--report-only`, `--no-thumbs`.
  Self-contained single-file output with embedded thumbnails, dark/light theme,
  searchable + filterable album grid. Editorial/liner-notes aesthetic with
  Fraunces, Geist, and JetBrains Mono typography.
- Pytest smoke suite (25 tests) for tagging, provider helpers, and report module.
- GitHub Actions CI for lint + tests on Python 3.10–3.13.
