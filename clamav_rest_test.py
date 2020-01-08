import unittest
from unittest.mock import patch

import clamd

import clamav_rest


class ClamAVRESTTestCase(unittest.TestCase):

    def setUp(self):
        clamav_rest.app.config['TESTING'] = True
        self.app = clamav_rest.app.test_client()

    def test_healthcheck_live(self):
        response = self.app.get('/health/live')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'OK')

    @patch('clamav_rest.cd.ping')
    def test_healthcheck_ready(self, ping):
        ping.return_value = 'PONG'

        response = self.app.get('/health/ready')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Service OK')

    @patch('clamav_rest.cd.ping')
    def test_healthcheck_no_service(self, ping):
        ping.side_effect = clamd.ConnectionError()

        response = self.app.get('/health/ready')

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data, b'Service Unavailable')

    @patch('clamav_rest.cd.ping')
    def test_healthcheck_unexpected_error(self, ping):
        ping.side_effect = Exception('Oops')

        response = self.app.get('/health/ready')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, b'Service Unavailable')

    @patch('clamav_rest.cd.ping')
    def test_healthcheck_unexpected_error_original(self, ping):
        ping.side_effect = Exception('Oops')

        response = self.app.get('/health/ready')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, b'Service Unavailable')

    def test_scan_endpoint_requires_post(self):
        response = self.app.get('/')

        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()
