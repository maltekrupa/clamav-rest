import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False

    CLAMAV_TXT_URI = "current.cvd.clamav.net"

    CLAMD_HOST = "localhost"
    CLAMD_PORT = 3310
    HOST = "0.0.0.0"
    PORT = int(os.environ.get('PORT', '8090'))


class ProductionConfig(BaseConfig):
    CLAMD_HOST = os.environ.get("CLAMD_HOST", "clamav")
