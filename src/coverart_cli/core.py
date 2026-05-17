"""Core workflow — iterate an album library, fetch + embed/sidecar cover art."""
from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

from coverart_cli.providers import CoverProvider, ProviderResult
from coverart_cli.tagging import (
    AUDIO_EXTS,
    AlbumMeta,
    embed_cover,
    find_sidecar,
    has_embedded_cover,
    read_album_meta,
    write_sidecar,
)

log = logging.getLogger(__name__)


@dataclass
class RunStats:
    albums_total: int = 0
    sidecar_already: int = 0
    fetched_from: dict[str, int] = field(default_factory=dict)
    not_found: int = 0
    files_embedded: int = 0
    files_already_embedded: int = 0
    errors: int = 0
    misses: list[tuple[Path, str]] = field(default_factory=list)

    def record_fetch(self, source: str) -> None:
        self.fetched_from[source] = self.fetched_from.get(source, 0) + 1


@dataclass
class RunOptions:
    """Knobs for a coverart run."""

    root: Path
    providers: list[CoverProvider]
    do_embed: bool = True
    do_sidecar: bool = True
    dry_run: bool = False
    fallback_to_dirnames: bool = True
    missing_csv: Path | None = None


def find_album_dirs(root: Path) -> list[Path]:
    """Return all directories under root that contain audio files (depth-first)."""
    albums: list[Path] = []
    for d in sorted(root.rglob("*")):
        if not d.is_dir() or d.name.startswith("."):
            continue
        try:
            if any(
                f.is_file() and f.suffix.lower() in AUDIO_EXTS
                for f in d.iterdir()
            ):
                albums.append(d)
        except (PermissionError, OSError) as e:
            log.warning("cannot read %s: %s", d, e)
    return albums


def album_meta_for(album_dir: Path, *, fallback_to_dirnames: bool) -> AlbumMeta | None:
    """Read album metadata: tags first, optional fallback to parent/dir name."""
    audio_files = sorted(
        f for f in album_dir.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTS
    )
    for f in audio_files:
        meta = read_album_meta(f)
        if meta:
            return meta
    if fallback_to_dirnames and album_dir.parent != album_dir:
        artist = album_dir.parent.name
        album = album_dir.name
        if artist and album and not artist.startswith("."):
            return AlbumMeta(artist=artist, album=album)
    return None


def process_album(album_dir: Path, opts: RunOptions, stats: RunStats) -> None:
    """Fetch + apply cover art for one album directory."""
    stats.albums_total += 1
    if opts.do_sidecar and find_sidecar(album_dir):
        stats.sidecar_already += 1
        log.info("[skip-sidecar] %s", album_dir.name)
        return

    meta = album_meta_for(album_dir, fallback_to_dirnames=opts.fallback_to_dirnames)
    if not meta:
        log.warning("[no-meta]  %s", album_dir)
        stats.misses.append((album_dir, "no readable tags or directory metadata"))
        stats.not_found += 1
        return

    result: ProviderResult | None = None
    for provider in opts.providers:
        result = provider.fetch(meta.artist, meta.album)
        if result:
            break

    if not result:
        log.info("[miss]     %s", meta)
        stats.misses.append((album_dir, f"not found: {meta}"))
        stats.not_found += 1
        return

    log.info("[%s] %s", result.source, meta)
    stats.record_fetch(result.source)

    if opts.dry_run:
        return

    if opts.do_sidecar:
        try:
            write_sidecar(album_dir, result.image_bytes)
        except OSError as e:
            log.error("sidecar write failed for %s: %s", album_dir, e)
            stats.errors += 1

    if opts.do_embed:
        audio_files = [
            f for f in album_dir.iterdir()
            if f.is_file() and f.suffix.lower() in AUDIO_EXTS
        ]
        for f in audio_files:
            if has_embedded_cover(f):
                stats.files_already_embedded += 1
                continue
            ok = embed_cover(f, result.image_bytes)
            if ok:
                stats.files_embedded += 1
            else:
                stats.errors += 1


def run(opts: RunOptions) -> RunStats:
    """Top-level: walk root, process every album directory."""
    stats = RunStats()
    if not opts.root.exists():
        raise FileNotFoundError(f"root not found: {opts.root}")
    if not opts.providers:
        raise ValueError("at least one provider must be configured")

    albums = find_album_dirs(opts.root)
    log.info("scanning %d album directories under %s", len(albums), opts.root)

    for album_dir in albums:
        try:
            process_album(album_dir, opts, stats)
        except Exception as e:  # defensive — keep batch running
            log.exception("unexpected error on %s: %s", album_dir, e)
            stats.errors += 1
            stats.misses.append((album_dir, f"crash: {e}"))

    if opts.missing_csv and stats.misses:
        _write_missing_csv(opts.missing_csv, stats.misses)
        log.info("wrote missing list: %s", opts.missing_csv)

    return stats


def _write_missing_csv(path: Path, misses: list[tuple[Path, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["album_path", "reason"])
        for album, reason in misses:
            w.writerow([str(album), reason])
