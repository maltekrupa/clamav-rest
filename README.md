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

## Developing locally (with docker)

Requirements:

- docker

Run the following to get up and running:

```
docker-compose up -d
```

After changing code, run the following command to renew the clamav-rest container:

```
docker-compose up -d --remove-orphans --build clamav_rest
```

## Developing locally (without docker)

Requirements:

- python3
- pipenv

Run the following to get up and running:

```
pipenv shell
pipenv install
```
