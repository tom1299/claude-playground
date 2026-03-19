import time
import uuid

import pytest
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from vul_functions.trivy import get_vulnerability_reports

NGINX_IMAGE = "nginx:1.21.0"
WAIT_INTERVAL_SECONDS = 10
WAIT_TIMEOUT_SECONDS = 300


def _wait_for_reports(namespace: str) -> None:
    elapsed = 0
    while elapsed < WAIT_TIMEOUT_SECONDS:
        reports = get_vulnerability_reports(namespace)
        if len(reports) > 0:
            return
        time.sleep(WAIT_INTERVAL_SECONDS)
        elapsed += WAIT_INTERVAL_SECONDS
    raise TimeoutError(
        f"No vulnerability reports generated in namespace '{namespace}' "
        f"within {WAIT_TIMEOUT_SECONDS}s"
    )


def _create_namespace(core_api: client.CoreV1Api, namespace: str) -> None:
    try:
        core_api.create_namespace(
            client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
        )
    except ApiException as e:
        if e.status != 409:
            raise


def _delete_namespace(core_api: client.CoreV1Api, namespace: str) -> None:
    try:
        core_api.delete_namespace(namespace)
    except ApiException as e:
        if e.status != 404:
            raise


def _deploy_nginx(apps_api: client.AppsV1Api, namespace: str) -> None:
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name="nginx", namespace=namespace),
        spec=client.V1DeploymentSpec(
            selector=client.V1LabelSelector(match_labels={"app": "nginx"}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(name="nginx", image=NGINX_IMAGE)
                    ]
                ),
            ),
        ),
    )
    try:
        apps_api.create_namespaced_deployment(namespace=namespace, body=deployment)
    except ApiException as e:
        if e.status != 409:
            raise


@pytest.fixture(scope="session")
def trivy_namespace():
    config.load_kube_config()
    core_api = client.CoreV1Api()
    apps_api = client.AppsV1Api()

    namespace = f"trivy-test-{uuid.uuid4().hex[:8]}"
    _create_namespace(core_api, namespace)
    _deploy_nginx(apps_api, namespace)
    _wait_for_reports(namespace)

    yield namespace

    _delete_namespace(core_api, namespace)


@pytest.fixture(scope="session")
def empty_trivy_namespace():
    config.load_kube_config()
    core_api = client.CoreV1Api()

    namespace = f"trivy-empty-{uuid.uuid4().hex[:8]}"
    _create_namespace(core_api, namespace)

    yield namespace

    _delete_namespace(core_api, namespace)


class TestGetVulnerabilityReports:
    def test_returns_non_empty_list(self, trivy_namespace):
        reports = get_vulnerability_reports(trivy_namespace)
        assert len(reports) >= 1

    def test_reports_are_dicts(self, trivy_namespace):
        reports = get_vulnerability_reports(trivy_namespace)
        for report in reports:
            assert isinstance(report, dict)

    def test_report_has_expected_keys(self, trivy_namespace):
        reports = get_vulnerability_reports(trivy_namespace)
        expected_keys = {"metadata", "report", "apiVersion", "kind"}
        for report in reports:
            assert expected_keys.issubset(report.keys())

    def test_report_has_critical_vulnerabilities(self, trivy_namespace):
        reports = get_vulnerability_reports(trivy_namespace)
        critical_counts = [
            r.get("report", {}).get("summary", {}).get("criticalCount", 0)
            for r in reports
        ]
        assert any(count > 0 for count in critical_counts)

    def test_nonexistent_namespace_raises_value_error(self):
        with pytest.raises(ValueError) as exc_info:
            get_vulnerability_reports("nonexistent-namespace-xyz-12345")
        assert exc_info.value.__cause__ is None
        assert exc_info.value.__context__ is None

    def test_empty_namespace_returns_empty_list(self, empty_trivy_namespace):
        reports = get_vulnerability_reports(empty_trivy_namespace)
        assert reports == []
