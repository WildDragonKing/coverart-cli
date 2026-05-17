"""Provider-level smoke tests (no network)."""
from __future__ import annotations

import pytest

from coverart_cli.providers.lastfm import LastFmProvider
from coverart_cli.providers.musicbrainz import MusicBrainzProvider


def test_lastfm_requires_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        LastFmProvider(api_key="")


def test_lastfm_best_image_picks_largest() -> None:
    images = [
        {"size": "small", "#text": "http://example.com/s.jpg"},
        {"size": "large", "#text": "http://example.com/l.jpg"},
        {"size": "extralarge", "#text": "http://example.com/xl.jpg"},
        {"size": "mega", "#text": "http://example.com/mega.jpg"},
    ]
    assert LastFmProvider._best_image(images) == "http://example.com/mega.jpg"


def test_lastfm_best_image_skips_placeholder() -> None:
    placeholder = "https://lastfm.freetls.fastly.net/i/u/2a96cbd8b46e442fc41c2b86b821562f.png"
    images = [{"size": "mega", "#text": placeholder}]
    assert LastFmProvider._best_image(images) is None


def test_lastfm_best_image_empty() -> None:
    assert LastFmProvider._best_image([]) is None
    assert LastFmProvider._best_image([{"size": "small", "#text": ""}]) is None


def test_musicbrainz_escape_strips_lucene_special_chars() -> None:
    assert MusicBrainzProvider._escape('Some "Album" (Deluxe)') == "Some  Album   Deluxe"
    assert MusicBrainzProvider._escape("Foo [Disc 1]") == "Foo  Disc 1"


def test_itunes_provider_instantiable() -> None:
    from coverart_cli.providers import ITunesProvider

    ITunesProvider()  # no key required


def test_deezer_provider_instantiable() -> None:
    from coverart_cli.providers import DeezerProvider

    DeezerProvider()


def test_deezer_escape_strips_quotes() -> None:
    from coverart_cli.providers import DeezerProvider

    assert DeezerProvider._escape('"Foo" bar') == "Foo  bar"
