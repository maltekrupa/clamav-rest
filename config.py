import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO')
CLAMD_HOST = os.environ.get('CLAMD_HOST', 'clamav')
CLAMD_PORT = int(os.environ.get('CLAMD_PORT', 3310))
