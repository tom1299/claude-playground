from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

TRIVY_GROUP = "aquasecurity.github.io"
TRIVY_VERSION = "v1alpha1"
TRIVY_PLURAL = "vulnerabilityreports"


def _check_namespace_exists(core_api: client.CoreV1Api, namespace: str) -> None:
    try:
        core_api.read_namespace(namespace)
    except ApiException as e:
        if e.status == 404:
            raise ValueError(f"Namespace '{namespace}' does not exist")
        raise


def get_vulnerability_reports(namespace: str) -> list[dict]:
    """Return all Trivy VulnerabilityReports in the given namespace as dicts.

    Raises:
        ValueError: If the namespace does not exist.
    """
    config.load_kube_config()
    core_api = client.CoreV1Api()
    _check_namespace_exists(core_api, namespace)

    custom_api = client.CustomObjectsApi()
    response = custom_api.list_namespaced_custom_object(
        TRIVY_GROUP, TRIVY_VERSION, namespace, TRIVY_PLURAL
    )
    return response["items"]
