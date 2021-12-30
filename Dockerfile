FROM golang:1.14-alpine AS builder

RUN apk update && apk add git

RUN go get github.com/jsha/minica


FROM python:3.8.12-alpine3.15

# Upgrade pip
RUN pip install --upgrade pip

# Create user and group
RUN addgroup -g 1000 -S certgenerator  \
    && adduser -u 1000 -S certgenerator -G certgenerator

USER certgenerator
WORKDIR /home/certgenerator

COPY --from=builder /go/bin/minica /usr/bin/minica


COPY --chown=certgenerator:certgenerator . .

RUN pip install  --user --no-cache-dir .
ENV PATH="/home/certgenerator/.local/bin:${PATH}"

ENTRYPOINT ["certgenerator"]
CMD ["--help"]



