# https://hub.docker.com/_/python/tags
# This should match what is in the second stage docker image
FROM cgr.dev/astronomer.io/python:3.14.7-dev AS builder

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv build

# check latest tags from https://hub.docker.com/_/python/tags
FROM cgr.dev/astronomer.io/python:3.14.7-dev

USER root
# upgrade apk packages
# update-ca-certificates regenerates /etc/ssl/certs/ca-certificates.crt so the patched trust store (PINF-1304) is what gets read
RUN apk upgrade && apk add --upgrade sqlite-libs ca-certificates && update-ca-certificates

# Upgrade pip

COPY --from=builder /app/dist/*.whl .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir *.whl && \
    pip uninstall -y pip setuptools

# uv is only needed at build time and its bundled root store is flagged by the eMudhra scanner, hence removing it.
RUN apk del uv 2>/dev/null || true; \
    rm -f /usr/bin/uv /usr/bin/uvx /usr/local/bin/uv /usr/local/bin/uvx

# Create user and group
RUN addgroup -g 1000 -S certgenerator  \
    && adduser -u 1000 -S certgenerator -G certgenerator

WORKDIR /certgenerator

ENV MINICA_VERSION=v1.1.4

RUN wget https://github.com/astronomer/minica/releases/download/$MINICA_VERSION/minica-alpine-linux-amd64-$MINICA_VERSION.tar.gz \
	&& tar -C /usr/bin/ -xzvf minica-alpine-linux-amd64-$MINICA_VERSION.tar.gz \
	&& rm minica-alpine-linux-amd64-$MINICA_VERSION.tar.gz

WORKDIR /tmp

USER certgenerator

ENTRYPOINT ["certgenerator"]

CMD ["--help"]
