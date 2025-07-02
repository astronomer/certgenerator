# https://hub.docker.com/_/python/tags
# This should match what is in the second stage docker image
FROM python:3.11 AS builder

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv build

# check latest tags from https://hub.docker.com/_/python/tags
FROM python:3.11.13-alpine3.22

# upgrade apk packages
RUN apk upgrade

# Upgrade pip
RUN pip install --upgrade pip

COPY --from=builder /app/dist/*.whl .

RUN pip install --no-cache-dir .

# Create user and group
RUN addgroup -g 1000 -S certgenerator  \
    && adduser -u 1000 -S certgenerator -G certgenerator

WORKDIR /certgenerator

ENV MINICA_VERSION=v1.1.1

RUN wget https://github.com/astronomer/minica/releases/download/$MINICA_VERSION/minica-alpine-linux-amd64-$MINICA_VERSION.tar.gz \
	&& tar -C /usr/bin/ -xzvf minica-alpine-linux-amd64-$MINICA_VERSION.tar.gz \
	&& rm minica-alpine-linux-amd64-$MINICA_VERSION.tar.gz

WORKDIR /tmp

USER certgenerator

ENTRYPOINT ["certgenerator"]

CMD ["--help"]
