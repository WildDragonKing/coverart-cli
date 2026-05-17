# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
