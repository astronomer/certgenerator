# cert_generator

cli to generate/update TLS secrets for kubernetes service.

# Usage

```shell
$ cert_generator --help
Usage: cert_generator [OPTIONS]

  cli to generate/update TLS secrets for kubernetes service.

Options:
  --hostname TEXT       provide hostname to generate certificate  [required]
  --secret-name TEXT    [required]
  --namespace TEXT      [required]
  --in-cluster BOOLEAN
  --help                Show this message and exit.
```

# Requirements

- minica
- Python 3.x
- PIP
- KUBECONFIG
