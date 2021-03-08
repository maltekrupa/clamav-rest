import logging
import sys
import timeit
from functools import wraps

from quart import Quart, request, jsonify, current_app, abort

import clamd

app = Quart(__name__)
app.config.from_pyfile('config.py')

logging.basicConfig(stream=sys.stdout, level=app.config['LOGLEVEL'])
logger = logging.getLogger('CLAMAV-REST')

try:
    cd = clamd.ClamdAsyncNetworkSocket(
        host=app.config['CLAMD_HOST'],
        port=app.config['CLAMD_PORT']
    )
except BaseException:
    logger.exception('error bootstrapping clamd for network socket')

# https://gitlab.com/pgjones/quart-auth/-/issues/6#note_460844029
def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        auth = request.authorization
        if (
            auth is not None and
            auth.type == "basic" and
            auth.username == current_app.config["AUTH_USERNAME"] and
            compare_digest(auth.password, current_app.config["AUTH_PASSWORD"])
        ):
            return await func(*args, **kwargs)
        else:
            abort(401)

    return wrapper


@auth_required
@app.route('/', methods=['POST'])
async def scan():
    files = await request.files
    if len(files) != 1:
        return 'Provide a single file', 400

    _, file_data = list(files.items())[0]

    logger.info('Scanning {file_name}'.format(
        file_name=file_data.filename
    ))

    start_time = timeit.default_timer()
    try:
        resp = await cd.instream(file_data)
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
def health_live():
    return 'OK', 200


# Readyness probe goes here
@app.route('/health/ready', methods=['GET'])
async def health_ready():
    try:
        clamd_response = await cd.ping()
        if 'PONG' in clamd_response:
            return 'Service OK'

        logger.error('expected PONG from clamd container')
        return 'Service Down', 502

    except clamd.ConnectionError:
        logger.error('clamd.ConnectionError')
        return 'Service Unavailable', 502

    except BaseException as e:
        logger.error(e)
        return 'Service Unavailable', 500
