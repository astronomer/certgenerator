FROM golang:1.14-alpine AS builder

RUN apk update && apk add git

RUN go get github.com/jsha/minica


FROM python:3.8.2-alpine

WORKDIR /certgenerator

COPY --from=builder /go/bin/minica /usr/bin/minica

COPY . .

RUN pip install -r requirements.txt

RUN pip --no-cache-dir install .

ENTRYPOINT ["/usr/local/bin/certgenerator"]
CMD ["--help"]