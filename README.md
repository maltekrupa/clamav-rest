# Container ready ClamAV REST interface

## Acknowledgment

This project was forked from [dit-clamav-rest](https://github.com/uktrade/dit-clamav-rest)
in mid 2019 and changed to fit my needs.

The initial introduction still stands:

> This is a python-based REST interface to ClamD inspired by https://github.com/solita/clamav-rest

## Quickstart

### Setup

After cloning the repository, you can use docker-compose to get a
working setup up and running.

```
git clone https://github.com/maltekrupa/clamav-rest.git
cd clamav-rest/examples/docker-compose
docker-compose up
```

Observe the health status of all services using `docker ps`. Clamd might take a
while on its first start because it needs to download new signatures.

### Usage

Send a file to the `/` endpoint via a HTTP POST request using the Content-Type
`multipart/form-data` and receive some JSON in return which contains information
about the infection state of the file you sent.

An example using `curl` and the local docker-compose setup to scan a file called
`example.pdf` would look like this:

```
curl -F 'data=@example.pdf' localhost:8080
```

The response will look something like this:

```
{"malware":false,"reason":null,"time":0.14232846899903961}
```

## Optional basic auth

If you want to secure the virus scanning endpoint (`POST /`) via basic
auth, you'll have to provide both environment variables `AUTH_USERNAME` and
`AUTH_PASSWORD` to make it work.

If only one of them is set, basic auth is still disabled!

## Health check endpoints

Two health check endpoints exist.

`GET /health/live` will always return a HTTP 200 as soon as the service is started.

`GET /health/ready` will return a HTTP 200 if `clamav-rest` can communicate with
`clamd` and a HTTP 502 in case it cannot communicate with `clamd`.

## Metrics

Some metrics are available at `GET /metrics`.

## Environment variables

| Environment variable | Required | Default | Purpose |
| -------------------- | -------- | ------- | ------- |
| LOGLEVEL             | false    | INFO    | Loglevel |
| CLAMD_HOST           | false    | clamav  | Hostname where to reach clamav container |
| CLAMD_PORT           | false    | 3310    | Port where to reach clamav container |
| LISTEN_HOST          | false    | 0.0.0.0 | IP to listen on inside container |
| LISTEN_PORT          | false    | 8080    | Port to listen on inside container |
| AUTH_USERNAME        | false    |         | Username for optional basic auth |
| AUTH_PASSWORD        | false    |         | Password for optional basic auth |
