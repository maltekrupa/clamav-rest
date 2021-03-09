from unittest.mock import patch

import pytest
import clamd

import clamav_rest


@pytest.mark.asyncio
async def test_healthcheck_live():
    client = clamav_rest.app.test_client()

    response = await client.get('/health/live')
    assert response.status_code == 200
    result = await response.get_data()
    assert result == b'OK'


@pytest.mark.asyncio
@patch('clamav_rest.cd.ping')
async def test_healthcheck_ready(ping):
    client = clamav_rest.app.test_client()
    ping.return_value = 'PONG'

    response = await client.get('/health/ready')
    assert response.status_code == 200
    result = await response.get_data()
    assert result == b'Service OK'


@pytest.mark.asyncio
@patch('clamav_rest.cd.ping')
async def test_healthcheck_no_service(ping):
    client = clamav_rest.app.test_client()
    ping.side_effect = clamd.ConnectionError()

    response = await client.get('/health/ready')

    assert response.status_code == 502
    result = await response.get_data()
    assert result == b'Service Unavailable'


@pytest.mark.asyncio
@patch('clamav_rest.cd.ping')
async def test_healthcheck_unexpected_error(ping):
    client = clamav_rest.app.test_client()
    ping.side_effect = Exception('Oops')

    response = await client.get('/health/ready')

    assert response.status_code == 500
    result = await response.get_data()
    assert result == b'Service Unavailable'


@pytest.mark.asyncio
async def test_scan_endpoint_requires_post():
    client = clamav_rest.app.test_client()

    response = await client.get('/')

    assert response.status_code == 405
