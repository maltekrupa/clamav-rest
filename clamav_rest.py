import logging
import sys
import timeit

from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from prometheus_flask_exporter.multiprocess import (
    GunicornInternalPrometheusMetrics
    )

import clamd

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config.from_pyfile('config.py')
metrics = GunicornInternalPrometheusMetrics(app)

logging.basicConfig(stream=sys.stdout, level=app.config['LOGLEVEL'])
logger = logging.getLogger('CLAMAV-REST')

try:
    cd = clamd.ClamdNetworkSocket(
        host=app.config['CLAMD_HOST'],
        port=app.config['CLAMD_PORT']
    )
except BaseException:
    logger.exception('error bootstrapping clamd for network socket')


@auth.verify_password
def verify_password(username, password):
    if app.config['AUTH_USERNAME'] and app.config['AUTH_PASSWORD_HASH']:
        if app.config['AUTH_USERNAME'] == username:
            return check_password_hash(
                app.config['AUTH_PASSWORD_HASH'],
                password)
        else:
            return False
    else:
        return True


@app.route('/', methods=['POST'])
@auth.login_required
def scan():
    if len(request.files) != 1:
        return 'Provide a single file', 400

    _, file_data = list(request.files.items())[0]

    logger.info('Scanning {file_name}'.format(
        file_name=file_data.filename
    ))

    start_time = timeit.default_timer()
    try:
        resp = cd.instream(file_data)
    except clamd.ConnectionError as err:
        logger.error('clamd.ConnectionError: {}'.format(err))
        return 'Service Unavailable', 502
    elapsed = timeit.default_timer() - start_time

    status, reason = resp['stream']

    response = {
        'malware': False if status == 'OK' else True,
        'reason': reason,
        'time': elapsed
    }

    logger.info(
            'Scanned {file_name}. Duration: {elapsed}. Infected: {status}'
            .format(
                file_name=file_data.filename,
                elapsed=elapsed,
                status=response['malware']
            )
    )

    return jsonify(response)

# Liveness probe goes here
@app.route('/health/live', methods=['GET'])
@metrics.do_not_track()
def health_live():
    return 'OK', 200

# Readyness probe goes here
@app.route('/health/ready', methods=['GET'])
@metrics.do_not_track()
def health_ready():
    try:
        clamd_response = cd.ping()
        if clamd_response == 'PONG':
            return 'Service OK'

        logger.error('expected PONG from clamd container')
        return 'Service Down', 502

    except clamd.ConnectionError:
        logger.error('clamd.ConnectionError')
        return 'Service Unavailable', 502

    except BaseException as e:
        logger.error(e)
        return 'Service Unavailable', 500
