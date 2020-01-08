gunicorn -w 1 -b ${LISTEN_HOST:-0.0.0.0}:${LISTEN_PORT:-8080} --timeout 1000 clamav_rest:app
