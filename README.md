# certgenerator

[![Build Status](https://circleci.com/gh/astronomer/certgenerator.svg?style=shield)](https://circleci.com/gh/astronomer/certgenerator)
[![GitHub release](https://img.shields.io/github/release/astronomer/certgenerator)](https://github.com/astronomer/certgenerator/releases/latest)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/astronomer/certgenerator/blob/main/.pre-commit-config.yaml)
![Docker Pulls](https://img.shields.io/docker/pulls/astronomerinc/ap-certgenerator.svg?maxAge=604800)

cli to generate/update TLS secrets for kubernetes service.

# Usage

```shell
$ certgenerator --help
Usage: certgenerator [OPTIONS]

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
- pip
- KUBECONFIG
