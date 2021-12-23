from unittest.mock import MagicMock
from certgenerator import *
import os
from click.testing import CliRunner
import json

host = "default.svc.cluster.local"
secret_name = "sample-pgbouncer-client-certificates"


def test_certgenerator_cli():
    runner = CliRunner()
    result = runner.invoke(main, "--help")
    assert result.exit_code == 0


def test_generate_tls_certs():
    generate_tls_certs(hostname=host)
    assert True == os.path.exists(host)


def test_create_and_patch_tls_secret_raise_exception():
    kube_client = MagicMock()
    kube_client.list_namespaced_secret = MagicMock()
    kube_client.create_namespaced_secret = MagicMock()
    string_data = tls_cert_path(host)
    ensure_conn_secret(
        kube_client, namespace="default", secret_name=secret_name, hostname=host
    )
    kube_client.create_namespaced_secret("default", body=string_data)
    kube_client.list_namespaced_secret.assert_called_once_with(
        "default",
        label_selector="component=sample-pgbouncer-client-certificates",
        limit=1,
    )
