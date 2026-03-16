#!/bin/bash

set -euo pipefail

CLUSTER_NAME="fix-vulnerabilies-skill-test"
NAMESPACE="test"
NGINX_DEPLOYMENT="nginx"
# Use an outdated nginx version to ensure vulnerabilities are detected
NGINX_IMAGE="nginx:1.21.0"
TRIVY_NAMESPACE="trivy-system"

cluster_exists() {
    kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"
}

create_cluster() {
    if cluster_exists; then
        echo "Cluster '${CLUSTER_NAME}' already exists, skipping creation."
        return
    fi

    echo "Creating kind cluster '${CLUSTER_NAME}'..."
    kind create cluster --name "${CLUSTER_NAME}"
}

install_trivy_operator() {
    echo "Installing trivy-operator..."
    helm repo add aqua https://aquasecurity.github.io/helm-charts/ --force-update
    helm repo update

    helm upgrade --install trivy-operator aqua/trivy-operator \
        --namespace "${TRIVY_NAMESPACE}" \
        --create-namespace \
        --set targetNamespaces="test" \
        --wait
}

verify_trivy_operator() {
    echo "Verifying trivy-operator is running..."
    kubectl rollout status deployment/trivy-operator \
        --namespace "${TRIVY_NAMESPACE}" \
        --timeout=120s
    echo "trivy-operator is running."
}

create_namespace() {
    if kubectl get namespace "${NAMESPACE}" &>/dev/null; then
        echo "Namespace '${NAMESPACE}' already exists."
        return
    fi

    echo "Creating namespace '${NAMESPACE}'..."
    kubectl create namespace "${NAMESPACE}"
}

delete_vulnerability_reports() {
    echo "Deleting existing vulnerability reports in namespace '${NAMESPACE}'..."
    kubectl delete vulnerabilityreports --all --namespace "${NAMESPACE}" 2>/dev/null || true
}

recycle_nginx_deployment() {
    if kubectl get deployment "${NGINX_DEPLOYMENT}" --namespace "${NAMESPACE}" &>/dev/null; then
        echo "Restarting existing nginx deployment..."
        kubectl rollout restart deployment/"${NGINX_DEPLOYMENT}" --namespace "${NAMESPACE}"
        return
    fi

    echo "Deploying nginx with image '${NGINX_IMAGE}'..."
    kubectl create deployment "${NGINX_DEPLOYMENT}" \
        --image="${NGINX_IMAGE}" \
        --namespace="${NAMESPACE}"
}

wait_for_vulnerability_report() {
    echo "Waiting for vulnerability reports to be generated (this may take a few minutes)..."

    local max_attempts=30
    local attempt=0
    local sleep_seconds=20

    while [ "${attempt}" -lt "${max_attempts}" ]; do
        attempt=$((attempt + 1))
        local report_count
        report_count=$(kubectl get vulnerabilityreports \
            --namespace "${NAMESPACE}" \
            --no-headers 2>/dev/null | wc -l)

        if [ "${report_count}" -gt 0 ]; then
            echo "Vulnerability reports found."
            return
        fi

        echo "Attempt ${attempt}/${max_attempts}: No reports yet, waiting ${sleep_seconds}s..."
        sleep "${sleep_seconds}"
    done

    echo "ERROR: Vulnerability reports were not generated in time."
    exit 1
}

confirm_vulnerabilities_detected() {
    echo "Confirming vulnerabilities are detected in reports..."

    local vuln_count
    vuln_count=$(kubectl get vulnerabilityreports \
        --namespace "${NAMESPACE}" \
        -o jsonpath='{.items[0].report.summary.criticalCount}')

    if [ "${vuln_count}" -gt 0 ]; then
        echo "Confirmed: ${vuln_count} critical vulnerabilities detected in first report."
        return
    fi

    echo "WARNING: No critical vulnerabilities detected. Check the reports manually."
    kubectl get vulnerabilityreports --namespace "${NAMESPACE}" -o wide
}

main() {
    create_cluster
    install_trivy_operator
    verify_trivy_operator
    create_namespace
    delete_vulnerability_reports
    recycle_nginx_deployment
    wait_for_vulnerability_report
    confirm_vulnerabilities_detected
    echo "Setup complete."
}

main
