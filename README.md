# Container ready ClamAV REST interface

## Acknowledgment

This project was forked from [dit-clamav-rest](https://github.com/uktrade/dit-clamav-rest)
and changed to fit my needs.

The initial introduction still stands:

```
This is a python-based REST interface to ClamD
inspired by https://github.com/solita/clamav-rest
```

## Intention

I needed a solution to check files for infections which could easily be deployed
to kubernetes.

Other solutions and my reasons for not using them:

- [solita](https://github.com/solita/clamav-rest) was too old (Springboot+JDK
from somewhere in 2016) and based on the JVM.
- [uktrade](https://github.com/uktrade/dit-clamav-rest) has a mandatory basic
auth.

## Running with docker-compose

Check the
[docker-compose.yml](https://github.com/temal-/clamav-rest/blob/master/docker-compose.yml)
for a working example with
[mk0x/docker-clamav:alpine](https://hub.docker.com/r/mk0x/docker-clamav) as
clamd backend.

A container image is available at
[dockerhub](https://hub.docker.com/r/temal/clamav-rest).

## Optional basic auth

If you want to secure the virus scanning endpoint (`POST` on `/`) via basic
auth, you'll have to provide both `AUTH_USERNAME` and `AUTH_PASSWORD` to make
this work.

If only one of them is set, basic auth is still disabled!

## Development

Requirements:

- python3
- pipenv
- docker

### Starting service via docker

Run the following to get up and running:

```
docker-compose up -d
```

### Rebuild container after change

After changing code, run the following command to renew the clamav-rest container:

```
docker-compose up -d --remove-orphans --build clamav_rest
```

### Run tests locally

To run the tests, do the following:

```
pipenv shell
pipenv install -d
pipenv run pytest
```

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
