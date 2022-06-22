import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO')
LOGJSON = os.environ.get('LOGJSON', True)
CLAMD_HOST = os.environ.get('CLAMD_HOST', 'clamav')
CLAMD_PORT = int(os.environ.get('CLAMD_PORT', 3310))

AUTH_USERNAME = os.environ.get('AUTH_USERNAME', None)
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', None)

MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))
