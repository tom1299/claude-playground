import urllib.request
import json


def get_image_labels(image: str, tag: str = "latest") -> dict:
    """
    Retrieve OCI image labels from a remote registry without pulling the image.

    Args:
        image: Full image name, e.g. "ghcr.io/tom1299/nginx"
        tag:   Tag or digest, e.g. "1.0.9" or "latest"

    Returns:
        dict of label key/value pairs
    """
    parts = image.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f"image must be a fully qualified name like 'registry/repository', got: {image!r}"
        )
    registry = parts[0]
    repo = parts[1]

    token = _get_token(registry, repo)
    config_digest = _get_config_digest(registry, repo, tag, token)
    return _get_labels_from_blob(registry, repo, config_digest, token)


def _get_token(registry: str, repo: str) -> str:
    token_url = f"https://{registry}/token?service={registry}&scope=repository:{repo}:pull"
    with urllib.request.urlopen(token_url) as resp:
        return json.loads(resp.read())["token"]


def _get_config_digest(registry: str, repo: str, tag: str, token: str) -> str:
    url = f"https://{registry}/v2/{repo}/manifests/{tag}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": (
            "application/vnd.docker.distribution.manifest.v2+json,"
            "application/vnd.oci.image.manifest.v1+json"
        ),
    })
    with urllib.request.urlopen(req) as resp:
        manifest = json.loads(resp.read())
    return manifest["config"]["digest"]


def _get_labels_from_blob(registry: str, repo: str, digest: str, token: str) -> dict:
    url = f"https://{registry}/v2/{repo}/blobs/{digest}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        config = json.loads(resp.read())
    return config.get("config", {}).get("Labels") or {}
