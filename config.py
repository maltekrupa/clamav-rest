from werkzeug.security import generate_password_hash
import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO')
CLAMD_HOST = os.environ.get('CLAMD_HOST', 'clamav')
CLAMD_PORT = int(os.environ.get('CLAMD_PORT', 3310))

AUTH_USERNAME = os.environ.get('AUTH_USERNAME', None)
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', None)
if AUTH_PASSWORD:
    AUTH_PASSWORD_HASH = generate_password_hash(AUTH_PASSWORD)
else:
    AUTH_PASSWORD_HASH = None
