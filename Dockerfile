FROM python:3.12-alpine3.18 AS build-image

ENV WORKDIR /app
ENV PYTHONUSERBASE $WORKDIR
ENV PATH=$WORKDIR/bin:$PATH

RUN apk add -U git musl-dev build-base
RUN pip install --upgrade pip pipenv

WORKDIR $WORKDIR
ADD . $WORKDIR

RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy


FROM python:3.12-alpine3.18 AS runtime-image

LABEL org.opencontainers.image.source=https://github.com/maltekrupa/clamav-rest

ENV WORKDIR /app
WORKDIR $WORKDIR
ENV PYTHONUSERBASE $WORKDIR
ENV PATH=$WORKDIR/bin:$PATH

ENV PORT 8080
EXPOSE $PORT

COPY --from=build-image /app /app/

CMD ["/app/bin/hypercorn", "-k", "uvloop", "-b", "0.0.0.0:8080", "clamav_rest:app"]
