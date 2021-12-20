"""
Generate SSL for pgbouncer service
"""
import os
import click
import logging
import sys
from subprocess import Popen, PIPE
from urllib.parse import quote, urlencode
import shutil
from kubernetes import client, config
import base64


# Configure logging. DEBUG level logs includes logging secrets,
# so it should not be used in production.
LOG_LEVEL = logging.INFO
if os.environ.get("DEBUG"):
    LOG_LEVEL = logging.DEBUG
logging.basicConfig(
    level=LOG_LEVEL,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Creates Kubernetes Client
def create_kube_client(in_cluster):
    """
    Load and store authentication and cluster information from kube-config
    file; if running inside a pod, use Kubernetes service account. Use that to
    instantiate Kubernetes client.
    """
    if in_cluster:
        logging.info("Using in cluster kubernetes configuration")
        config.load_incluster_config()
    else:
        logging.info("Using kubectl kubernetes configuration")
        config.load_kube_config()
    return client.CoreV1Api()


def cleanup(folder_name=""):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)


# Generate  TLS certificate
def generate_tls_certs(hostname):
    logging.info(f"Cleaning Up any pre-created folder with hostname {hostname}")
    cleanup(folder_name=hostname)
    command = [f"minica -domains {hostname}"]
    generate_tls = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    generate_tls.communicate()
    return_code = generate_tls.poll()
    if return_code == 0:
        print("\u2705", "certificate generated successfully")
    else:
        print(f"Failed to execute command {command} with exit code {return_code}")
        sys.exit(2)


# Create k8s TLS secret
def create_k8s_secret(kube, namespace, secret_name, string_data):
    """Create the Kubernetes secret for Pgbouncer."""
    metadata = client.V1ObjectMeta(name=secret_name, labels={"component": secret_name})

    body = client.V1Secret(
        api_version="v1", kind="Secret", metadata=metadata, data=string_data
    )
    try:
        kube.create_namespaced_secret(namespace, body)
        logging.info("Pgbouncer TLS secret created successfully")
    except Exception as e:
        logging.exception(e)
        logging.info("Error creating secret")


# Patch k8s TLS secret if exists
def patch_k8s_secret(kube, namespace, secret_name, string_data):
    """Patch the existing Kubernetes secret for Pgbouncer."""
    metadata = client.V1ObjectMeta(labels={"component": secret_name})

    body = client.V1Secret(
        api_version="v1",
        kind="Secret",
        type="Opaque",
        metadata=metadata,
        data=string_data,
    )
    try:
        kube.patch_namespaced_secret(secret_name, namespace, body)
        logging.info("Pgbouncer TLS secret patched successfully")
    except Exception as e:
        logging.exception(e)
        logging.info("Error patching TLS secret")


def tls_cert_path(cert_path):
    # this should obviously go as function
    cert = open(f"{cert_path}/" + "cert.pem", "rb").read()
    cert_encoded = base64.b64encode(cert).decode("ascii")
    key = open(f"{cert_path}/" + "key.pem", "rb").read()
    key_encoded = base64.b64encode(key).decode("ascii")
    string_data = {"tls.crt": cert_encoded, "tls.key": key_encoded}
    return string_data


def ensure_conn_secret(
    kube,
    namespace,
    secret_name,
    hostname,
):
    """Create/update Kubernetes secret for Pgbouncer."""
    # Search for Secret
    kwargs = dict(label_selector=f"component={secret_name}", limit=1)

    string_data = tls_cert_path(cert_path=hostname)

    try:
        secrets = kube.list_namespaced_secret(namespace, **kwargs)
        if len(secrets.items) != 1:
            logging.info("Pgbouncer TLS Secret does not exist, creating...")
            create_k8s_secret(kube, namespace, secret_name, string_data)
        else:
            logging.info("Pgbouncer Secret exists, patching...")
            patch_k8s_secret(kube, namespace, secret_name, string_data)
    except Exception as e:
        logging.exception(e)


@click.command()
@click.option(
    "--hostname",
    envvar="HOSTNAME",
    help="hostname/servicename to generate certificate",
    required=True,
)
@click.option("--secret-name", envvar="SECRET_NAME", required=True)
@click.option("--namespace", envvar="NAMESPACE", required=True)
@click.option("--in-cluster", envvar="IN_CLUSTER", type=bool, default=False)
def main(secret_name, namespace, in_cluster, hostname):
    """cli to generate/update TLS secrets for kubernetes service."""
    logging.info("Creating TLS  client certs")
    minica_certs = generate_tls_certs(hostname)
    logging.info("Creating Kubernetes client")
    kube_client = create_kube_client(in_cluster)
    logging.info("Kube client created")
    ensure_conn_secret(
        kube_client, secret_name=secret_name, namespace=namespace, hostname=hostname
    )


if __name__ == "__main__":
    main()
