import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO')
CLAMD_HOST = os.environ.get('CLAMD_HOST', 'localhost')
CLAMD_PORT = int(os.environ.get('CLAMD_PORT', 3310))
LISTEN_HOST = os.environ.get("HOST", '0.0.0.0')
LISTEN_PORT = int(os.environ.get('PORT', 8080))
