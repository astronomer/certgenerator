from pytest_kind import KindCluster
from pytest import fixture, mark
from pykube import Pod, Secret
import operator
import time


@fixture(scope="session")
def kind_cluster():
    cluster = KindCluster("certgenerator")
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