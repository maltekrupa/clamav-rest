import logging
import sys
import timeit
from functools import wraps
from secrets import compare_digest

from quart import Quart, request, jsonify, current_app, abort
from aioprometheus import Counter, Histogram, Registry, render

import clamd

app = Quart(__name__)
app.config.from_pyfile('config.py')

# configure metrics
app.registry = Registry()
app.request_counter = Counter('requests', 'Number of overall requests.')
app.registry.register(app.request_counter)
app.scan_counter = Counter('scans', 'Number of overall virus scans.')
app.registry.register(app.scan_counter)
app.infection_counter = Counter('infections', 'Number of infected files found.')
app.registry.register(app.infection_counter)
app.scan_duration_histogram = Histogram('scan_duration', 'Histogram over virus scan duration.')
app.registry.register(app.scan_duration_histogram)

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
        if (
            current_app.config['AUTH_USERNAME'] and
            current_app.config['AUTH_PASSWORD']
        ):
            auth = request.authorization
            if (
                auth is not None and
                auth.type == 'basic' and
                auth.username == current_app.config['AUTH_USERNAME'] and
                compare_digest(auth.password, current_app.config['AUTH_PASSWORD'])
            ):
                return await func(*args, **kwargs)
            else:
                abort(401)
        else:
            return await func(*args, **kwargs)
    return wrapper


@app.route('/', methods=['POST'])
@auth_required
async def scan():
    # metric
    app.request_counter.inc({'path': '/'})

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

    # metric
    app.scan_duration_histogram.observe({'time': 'scan_duration'}, elapsed)

    status, reason = resp['stream']

    # metric
    if status != 'OK':
        app.infection_counter.inc({'path': '/'})

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

    # metric
    app.scan_counter.inc({'path': '/'})

    return jsonify(response)


# metrics endpoint
@app.route('/metrics')
async def handle_metrics():
    content, http_headers = render(app.registry, request.headers.getlist('accept'))
    return content, http_headers


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
