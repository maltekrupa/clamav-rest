FROM python:3.13-alpine3.21 AS build-image

RUN apk add -U git uv

WORKDIR /app
ADD . .

RUN uv sync --locked


FROM python:3.13-alpine3.21 AS runtime-image

LABEL org.opencontainers.image.source=https://github.com/maltekrupa/clamav-rest

WORKDIR /app

ENV PORT=8080
EXPOSE $PORT

COPY --from=build-image /app /app/

CMD ["/app/.venv/bin/hypercorn", "-k", "uvloop", "-b", "0.0.0.0:8080", "clamav_rest:app"]
