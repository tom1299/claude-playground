import json
from unittest.mock import MagicMock, patch

import pytest

from vul_functions.registry import (
    _get_config_digest,
    _get_labels_from_blob,
    _get_token,
    get_image_labels,
)


def _mock_urlopen(response_data: dict):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


@patch("urllib.request.urlopen")
def test_get_token(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen({"token": "abc123"})
    token = _get_token("ghcr.io", "tom1299/nginx")
    assert token == "abc123"


@patch("urllib.request.urlopen")
def test_get_config_digest(mock_urlopen):
    manifest = {"config": {"digest": "sha256:deadbeef"}}
    mock_urlopen.return_value = _mock_urlopen(manifest)
    digest = _get_config_digest("ghcr.io", "tom1299/nginx", "latest", "tok")
    assert digest == "sha256:deadbeef"


@patch("urllib.request.urlopen")
def test_get_labels_from_blob(mock_urlopen):
    blob = {"config": {"Labels": {"version": "1.0", "maintainer": "alice"}}}
    mock_urlopen.return_value = _mock_urlopen(blob)
    labels = _get_labels_from_blob("ghcr.io", "tom1299/nginx", "sha256:deadbeef", "tok")
    assert labels == {"version": "1.0", "maintainer": "alice"}


@patch("urllib.request.urlopen")
def test_get_labels_from_blob_no_labels(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen({"config": {}})
    labels = _get_labels_from_blob("ghcr.io", "tom1299/nginx", "sha256:deadbeef", "tok")
    assert labels == {}


@patch("vul_functions.registry._get_labels_from_blob")
@patch("vul_functions.registry._get_config_digest")
@patch("vul_functions.registry._get_token")
def test_get_image_labels(mock_token, mock_digest, mock_labels):
    mock_token.return_value = "tok"
    mock_digest.return_value = "sha256:deadbeef"
    mock_labels.return_value = {"env": "prod"}

    result = get_image_labels("ghcr.io/tom1299/nginx", "1.0.9")

    mock_token.assert_called_once_with("ghcr.io", "tom1299/nginx")
    mock_digest.assert_called_once_with("ghcr.io", "tom1299/nginx", "1.0.9", "tok")
    mock_labels.assert_called_once_with("ghcr.io", "tom1299/nginx", "sha256:deadbeef", "tok")
    assert result == {"env": "prod"}
