"""Deezer public search API — no key required."""
from __future__ import annotations

import json
import logging
import urllib.parse

from coverart_cli.providers.base import CoverProvider, ProviderResult

log = logging.getLogger(__name__)

DEEZER_SEARCH = "https://api.deezer.com/search/album"


class DeezerProvider(CoverProvider):
    """Search Deezer's public catalogue. Uses the cover_xl (1000×1000) URL."""

    name = "deezer"

    def fetch(self, artist: str, album: str) -> ProviderResult | None:
        query = f'artist:"{self._escape(artist)}" album:"{self._escape(album)}"'
        url = DEEZER_SEARCH + "?" + urllib.parse.urlencode({"q": query, "limit": "5"})
        raw = self._http_get(url)
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None

        for hit in data.get("data", []):
            img_url = hit.get("cover_xl") or hit.get("cover_big")
            if not img_url:
                continue
            img = self._http_get(img_url, timeout=25)
            if img and len(img) >= 2000:
                return ProviderResult(
                    image_bytes=img, source=self.name, image_url=img_url
                )
        return None

    @staticmethod
    def _escape(s: str) -> str:
        return s.replace('"', " ").strip()
