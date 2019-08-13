FROM python:3.7.4-alpine AS build-image

ENV WORKDIR /app
ENV PYTHONUSERBASE $WORKDIR
ENV PATH=$WORKDIR/bin:$PATH

RUN pip install --upgrade pip pipenv

WORKDIR $WORKDIR
ADD . $WORKDIR

RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy


FROM python:3.7.4-alpine AS runtime-image

ENV WORKDIR /app
WORKDIR $WORKDIR
ENV PYTHONUSERBASE $WORKDIR
ENV PATH=$WORKDIR/bin:$PATH

ENV PORT 8080
EXPOSE $PORT

COPY --from=build-image /app /app/

CMD ["/bin/sh", "/app/run.sh"]
