"""MusicBrainz + Cover Art Archive provider."""
from __future__ import annotations

import json
import logging
import time
import urllib.parse

from coverart_cli.providers.base import CoverProvider, ProviderResult

log = logging.getLogger(__name__)

MB_API = "https://musicbrainz.org/ws/2/"
CAA_API = "https://coverartarchive.org/"
# MusicBrainz requires 1 req/s. Be polite.
MB_MIN_DELAY = 1.1


class MusicBrainzProvider(CoverProvider):
    name = "musicbrainz"

    def __init__(self, user_agent: str = "coverart-cli/0.1.0", search_limit: int = 5) -> None:
        # MusicBrainz REQUIRES a meaningful UA with contact info; nudge users.
        if "contact" not in user_agent.lower() and "@" not in user_agent:
            log.debug("musicbrainz UA should include contact info per their TOS")
        self.user_agent = user_agent
        self.search_limit = search_limit
        self._last_request = 0.0

    def fetch(self, artist: str, album: str) -> ProviderResult | None:
        self._respect_rate_limit()
        rgs = self._search_release_groups(artist, album)
        if not rgs:
            return None
        for rg in rgs:
            mbid = rg.get("id")
            if not mbid:
                continue
            for endpoint in ("release-group", "release"):
                # release-group front first (album-level), then individual release fallback
                if endpoint == "release":
                    continue  # release-group is usually enough; skip per-release loop
                caa_url = f"{CAA_API}{endpoint}/{mbid}/front-1000"
                img = self._http_get(caa_url, timeout=25)
                if img and len(img) > 2000:
                    return ProviderResult(image_bytes=img, source=self.name, image_url=caa_url)
        return None

    def _search_release_groups(self, artist: str, album: str) -> list[dict]:
        query = f'artist:"{self._escape(artist)}" AND release:"{self._escape(album)}"'
        url = MB_API + "release-group/?" + urllib.parse.urlencode({
            "query": query,
            "fmt": "json",
            "limit": str(self.search_limit),
        })
        raw = self._http_get(url)
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        return data.get("release-groups", [])

    @staticmethod
    def _escape(s: str) -> str:
        # MusicBrainz Lucene-style query — escape special chars
        for ch in ('"', "\\", "(", ")", "[", "]", "{", "}"):
            s = s.replace(ch, " ")
        return s.strip()

    def _respect_rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < MB_MIN_DELAY:
            time.sleep(MB_MIN_DELAY - elapsed)
        self._last_request = time.time()
