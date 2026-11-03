from pytest_kind import KindCluster
from pytest import fixture, mark
from pykube import Pod, Secret
import os
import operator
import platform
import time
from pathlib import Path

# The kind release has to ship the kindest/node image for KUBE_VERSION.
KIND_VERSION = os.getenv(
    "KIND_VERSION", "v0.33.0"
)  # https://github.com/kubernetes-sigs/kind/releases
KUBE_VERSION = os.getenv(
    "KUBE_VERSION", "1.37.0"
)  # https://hub.docker.com/r/kindest/node/tags
IMAGE = f"kindest/node:v{KUBE_VERSION}"
# pytest_kind is loaded as a pytest plugin before this file, so it has already read its own KIND_VERSION (v0.17.0 by default)
# and KUBECTL_VERSION (v1.25.3 by default). Setting those variables here has no effect, so pass the kind binary path and
# download URL explicitly. KUBECTL_VERSION still has to be exported before pytest starts (the CI job does this).
KIND_ARCH = "arm64" if platform.machine() in ("arm64", "aarch64") else "amd64"
KIND_PATH = Path(".pytest-kind") / f"kind-{KIND_VERSION}-{KIND_ARCH}"
os.environ.setdefault(
    "KIND_DOWNLOAD_URL",
    f"https://github.com/kubernetes-sigs/kind/releases/download/{KIND_VERSION}/kind-{platform.system().lower()}-{KIND_ARCH}",
)


@fixture(scope="session")
def kind_cluster():
    cluster = KindCluster(name="certgenerator", image=IMAGE, kind_path=KIND_PATH)
    cluster.create()

    yield cluster
    cluster.delete()


def test_k8s_cluster(kind_cluster):
    print(kind_cluster.kubeconfig_path)
    assert kind_cluster.name == "certgenerator"


@mark.skip(reason="currently not needed")
def test_k8s_api_version(kind_cluster):
    assert kind_cluster.api.version == ("1", "20")


def test_k8s_pod(kind_cluster):
    kind_cluster.load_docker_image("ap-certgenerator")
    time.sleep(60)
    kind_cluster.kubectl("create", "ns", "astronomer")
    kind_cluster.kubectl("apply", "-f", "rbac.yaml")
    kind_cluster.kubectl("apply", "-f", "generate_ssl.yaml")
    time.sleep(60)
    pods = Pod.objects(kind_cluster.api).filter(selector="component=certgenerator")
    for pod in pods:
        assert "Completed" in pod.obj["status"]["phase"]


def test_k8s_tls_secret(kind_cluster):
    secrets = Secret.objects(kind_cluster.api).filter(
        namespace="astronomer",
        selector="component=certgenerator-pgbouncer-client-certificates",
    )
    for secret in secrets:
        assert (
            "certgenerator-pgbouncer-client-certificates"
            == secret.obj["metadata"]["name"]
        )
