# Gunicorn
import os

# Prometheus
from prometheus_flask_exporter.multiprocess import (
    GunicornInternalPrometheusMetrics
    )

host = os.environ.get('LISTEN_HOST', '0.0.0.0')
port = int(os.environ.get('LISTEN_PORT', 8080))

bind = '{}:{}'.format(host, port)
workers = 2
threads = 4
worker_class = 'gthread'
timeout = 1000


def child_exit(server, worker):
    GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(
            worker.pid)
