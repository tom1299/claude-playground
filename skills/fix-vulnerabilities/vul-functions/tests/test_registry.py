import pytest

from vul_functions.registry import (
    get_image_digest,
    get_annotations,
    get_token, get_image_labels,
)

@pytest.mark.dependency()
def test_get_token():
    token = get_token("ghcr.io", "tom1299/nginx")
    assert token is not None
    assert len(token) > 0

@pytest.mark.dependency(depends=["test_get_token"])
def test_get_config_digest():
    token = get_token("ghcr.io", "tom1299/nginx")
    digest = get_image_digest("ghcr.io", "tom1299/nginx", "1.0.9", token)
    assert digest is not None
    assert len(digest) > 0

@pytest.mark.dependency(depends=["test_get_config_digest"])
def test_get_annotations():
    token = get_token("ghcr.io", "tom1299/nginx")
    digest = get_image_digest("ghcr.io", "tom1299/nginx", "1.0.9", token)
    annotations = get_annotations("ghcr.io", "tom1299/nginx", digest, token)
    assert annotations is not None
    assert annotations.get("org.opencontainers.image.source") == "https://github.com/tom1299/nginx"

@pytest.mark.dependency(depends=["test_get_annotations"])
def test_get_image_labels():
    labels = get_image_labels("ghcr.io/tom1299/nginx", "1.0.9")
    assert labels is not None
    assert labels.get("org.opencontainers.image.source") == "https://github.com/tom1299/nginx"

@pytest.mark.dependency(depends=["test_get_image_labels"])
@pytest.mark.xfail(reason="Implementation for images without registry is incomplete")
def test_get_image_labels_docker_hub():
    # Images without registry should us "docker.io" as the default registry
    labels = get_image_labels("busybox", "1.36")
    assert labels is not None
