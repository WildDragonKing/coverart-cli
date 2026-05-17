"""Optional TOML config file for default CLI values.

Resolution order (later wins):
  1. Built-in defaults (from argparse)
  2. ~/.config/coverart-cli/config.toml  (XDG: $XDG_CONFIG_HOME or ~/.config)
  3. ./coverart.toml                     (working directory)
  4. --config PATH (explicit)
  5. Command-line flags
  6. Environment variables  (e.g. LASTFM_API_KEY)

Example file (all keys optional):

    # ~/.config/coverart-cli/config.toml
    lastfm_key  = "your-key"
    no_lastfm   = false
    no_itunes   = false
    no_deezer   = false
    no_musicbrainz = false
    no_embed    = false
    no_sidecar  = false
    min_bytes   = 30000
    replace_smaller = true
    user_agent  = "coverart-cli (mailto:you@example.com)"
"""
from __future__ import annotations

import logging
import os
import tomllib
from pathlib import Path

log = logging.getLogger(__name__)

# Keys we accept in the config file — must match argparse `dest` names.
ALLOWED_KEYS: frozenset[str] = frozenset({
    "lastfm_key",
    "no_lastfm",
    "no_itunes",
    "no_deezer",
    "no_musicbrainz",
    "user_agent",
    "no_embed",
    "no_sidecar",
    "no_fallback_dirnames",
    "min_bytes",
    "replace_smaller",
    "dry_run",
    "missing_csv",
    "report_html",
    "no_thumbs",
    "report_only",
})


def default_config_paths() -> list[Path]:
    """Return the list of config paths to check, lowest-precedence first."""
    paths: list[Path] = []
    xdg = os.environ.get("XDG_CONFIG_HOME")
    config_root = Path(xdg) if xdg else Path.home() / ".config"
    paths.append(config_root / "coverart-cli" / "config.toml")
    paths.append(Path.cwd() / "coverart.toml")
    return paths


def load_config(explicit_path: Path | None = None) -> dict:
    """Merge config from default locations (and the explicit path, if given).

    Higher-precedence sources overwrite earlier ones. Unknown keys are dropped
    with a warning so a typo doesn't silently change behaviour.
    """
    paths = default_config_paths()
    if explicit_path is not None:
        paths.append(explicit_path)

    merged: dict = {}
    for p in paths:
        if not p.is_file():
            continue
        try:
            with p.open("rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            log.warning("ignoring config %s: %s", p, e)
            continue
        for key, value in data.items():
            if key not in ALLOWED_KEYS:
                log.warning("ignoring unknown config key %r in %s", key, p)
                continue
            merged[key] = value
    return merged
