import pytest

from opportunity_compass.tools import _validate_public_https_url, _VisibleTextParser


def test_visible_text_parser_excludes_scripts_and_styles() -> None:
    parser = _VisibleTextParser()
    parser.feed(
        "<html><head><title>Real title</title><style>secret css</style></head>"
        "<body><h1>Visible</h1><script>steal()</script><p>Evidence</p></body></html>"
    )

    assert "Real title" == "".join(parser.title_parts)
    assert "Visible" in " ".join(parser.parts)
    assert "Evidence" in " ".join(parser.parts)
    assert "secret css" not in " ".join(parser.parts)
    assert "steal" not in " ".join(parser.parts)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://localhost/private",
        "https://127.0.0.1/private",
        "file:///etc/passwd",
    ],
)
def test_private_or_non_https_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        _validate_public_https_url(url)
