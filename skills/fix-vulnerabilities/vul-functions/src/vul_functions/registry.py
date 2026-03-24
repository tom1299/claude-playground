import urllib.request
import json
from urllib.request import Request


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
    if len(parts) == 2 and parts[0] and parts[1]:
        registry = parts[0]
        repo = parts[1]
    else:
        # Bare image name (e.g. "busybox") — default to Docker Hub
        registry = "docker.io"
        repo = f"library/{image}"

    token = get_token(registry, repo)
    image_digest = get_image_digest(registry, repo, tag, token)
    return get_annotations(registry, repo, image_digest, token)


def get_token(registry: str, repo: str) -> str:
    if registry == "docker.io":
        token_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"
    else:
        token_url = f"https://{registry}/token?service={registry}&scope=repository:{repo}:pull"
    with urllib.request.urlopen(token_url) as resp:
        return json.loads(resp.read())["token"]


def get_image_digest(registry: str, repo: str, tag: str, token: str) -> str:
    req = get_manifest(registry, repo, tag, token)
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read())

    for manifest in response.get("manifests", []):
        if manifest.get("digest"):
            return manifest["digest"]
    else:
        raise ValueError(f"Config digest not found in manifest for {registry}/{repo}:{tag}")

def get_annotations(registry: str, repo: str, tag: str, token: str) -> dict:
    req = get_manifest(registry, repo, tag, token)
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read())
    return response.get("annotations", {})


def get_manifest(registry: str, repo: str, manifest_identifier: str, token: str) -> Request:
    api_host = "registry-1.docker.io" if registry == "docker.io" else registry
    url = f"https://{api_host}/v2/{repo}/manifests/{manifest_identifier}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": (
            "application/vnd.docker.distribution.manifest.v2+json,"
            "application/vnd.oci.image.manifest.v1+json,"
            "application/vnd.oci.image.index.v1+json"
        ),
    })
    return req
