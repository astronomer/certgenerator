FROM golang:1.14-alpine AS builder

RUN apk update && apk add git

RUN go get github.com/jsha/minica

# check latest tags from https://hub.docker.com/_/python/tags
FROM python:3.9.22-alpine3.22

# upgrade apk packages
RUN apk upgrade

# Upgrade pip
RUN pip install --upgrade pip

# Create user and group
RUN addgroup -g 1000 -S certgenerator  \
    && adduser -u 1000 -S certgenerator -G certgenerator

WORKDIR /certgenerator

COPY --from=builder /go/bin/minica /usr/bin/minica

COPY --chown=certgenerator:certgenerator . .

RUN pip install --no-cache-dir .

WORKDIR /tmp

USER certgenerator

ENTRYPOINT ["certgenerator"]

CMD ["--help"]
