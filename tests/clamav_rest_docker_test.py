import pytest
import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError


# These values mirror the basic auth credentials from the docker-compose file
AUTH_USERNAME = 'foo'
AUTH_PASSWORD = 'bar'

auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_PASSWORD)
virus_file = {'file': (
    'OHOH_report.txt',
    r'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    )}
plain_file = {'file': ('report.txt', 'WE NEED MORE MONEYZ!\n')}


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope='session')
def http_service(docker_ip, docker_services):
    '''Ensure that HTTP service is up and responsive.'''

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for('clamav_rest', 8080)
    url = 'http://{}:{}'.format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=60, pause=5, check=lambda: is_responsive(url + '/health/ready')
    )
    return url


def test_plain_needs_post(http_service):
    response = requests.get(http_service)

    assert response.status_code == 405


def test_plain_post_is_unavailable(http_service):
    response = requests.post(http_service)

    assert response.status_code == 400


def test_plain_post_works_with_file(http_service):
    response = requests.post(http_service, files=plain_file)

    json = response.json()
    assert response.status_code == 200
    assert not json['malware']


def test_plain_post_works_with_virus(http_service):
    response = requests.post(http_service, files=virus_file)

    json = response.json()
    assert response.status_code == 200
    assert json['malware']
    assert json['reason'] == 'Win.Test.EICAR_HDB-1'


@pytest.fixture(scope='session')
def http_service_auth(docker_ip, docker_services):
    '''Ensure that HTTP service with auth is up and responsive.'''

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for('clamav_rest_auth', 8080)
    url = 'http://{}:{}'.format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=60, pause=5, check=lambda: is_responsive(url + '/health/ready')
    )
    return url


def test_auth_needs_post(http_service_auth):
    response = requests.get(http_service_auth, auth=auth)

    assert response.status_code == 405


def test_auth_post_is_unavailable(http_service_auth):
    response = requests.post(http_service_auth, auth=auth)

    assert response.status_code == 400


def test_auth_post_works_with_file(http_service_auth):
    response = requests.post(http_service_auth, auth=auth, files=plain_file)

    json = response.json()
    assert response.status_code == 200
    assert not json['malware']


def test_auth_post_works_with_virus(http_service_auth):
    response = requests.post(http_service_auth, auth=auth, files=virus_file)

    json = response.json()
    assert response.status_code == 200
    assert json['malware']
    assert json['reason'] == 'Win.Test.EICAR_HDB-1'


def test_auth_post_fails_unauthenticated_with_file(http_service_auth):
    response = requests.post(http_service_auth, files=plain_file)

    assert response.status_code == 401


def test_auth_post_fails_unauthenticated_with_virus(http_service_auth):
    response = requests.post(http_service_auth, files=virus_file)

    assert response.status_code == 401


def test_auth_liveness_endpoint_is_unauthenticated(http_service_auth):
    response = requests.get(http_service_auth + '/health/live')

    assert response.status_code == 200


def test_auth_prometheus_endpoint_is_unauthenticated(http_service_auth):
    response = requests.get(http_service_auth + '/metrics')

    assert response.status_code == 200


@pytest.fixture(scope='session')
def http_service_auth_defunct(docker_ip, docker_services):
    '''
    Ensure that HTTP service with wrongly configured auth is up and responsive.
   '''

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for('clamav_rest_auth_defunct', 8080)
    url = 'http://{}:{}'.format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=60, pause=5, check=lambda: is_responsive(url + '/health/ready')
    )
    return url


def test_auth_defunct_needs_post(http_service_auth_defunct):
    response = requests.get(http_service_auth_defunct, auth=auth)

    assert response.status_code == 405


def test_auth_defunct_post_is_unavailable(http_service_auth_defunct):
    response = requests.post(http_service_auth_defunct, auth=auth)

    assert response.status_code == 400


def test_auth_defunct_post_works_with_file(http_service_auth_defunct):
    response = requests.post(http_service_auth_defunct, files=plain_file)

    json = response.json()
    assert response.status_code == 200
    assert not json['malware']


def test_auth_defunct_post_works_with_virus(http_service_auth_defunct):
    response = requests.post(http_service_auth_defunct, files=virus_file)

    json = response.json()
    assert response.status_code == 200
    assert json['malware']
    assert json['reason'] == 'Win.Test.EICAR_HDB-1'


def test_auth_defunct_post_works_unauthenticated_with_file(http_service_auth_defunct):
    response = requests.post(http_service_auth_defunct, files=plain_file)

    json = response.json()
    assert response.status_code == 200
    assert not json['malware']


def test_auth_defunct_post_works_unauthenticated_with_virus(http_service_auth_defunct):
    response = requests.post(http_service_auth_defunct, files=virus_file)

    json = response.json()
    assert response.status_code == 200
    assert json['malware']
    assert json['reason'] == 'Win.Test.EICAR_HDB-1'


def test_auth_defunct_liveness_endpoint_is_unauthenticated(http_service_auth_defunct):
    response = requests.get(http_service_auth_defunct + '/health/live')

    assert response.status_code == 200


def test_auth_defunct_prometheus_endpoint_is_unauthenticated(http_service_auth_defunct):
    response = requests.get(http_service_auth_defunct + '/metrics')

    assert response.status_code == 200
