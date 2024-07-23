import pytest
import requests
from requests.exceptions import ConnectionError


def is_docker_running():
    import docker

    run_status = False
    try:
        client = docker.from_env()
        run_status = True
    except docker.errors.DockerException:
        run_status = False
    return run_status


is_docker_available = pytest.mark.skipif(not is_docker_running(), reason="docker is not running")


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def check_option_with_docker(pytestconfig):
    if "with_docker" not in pytestconfig.getoption("-m"):
        print('\noption must be passed explicitly: -m "with_docker"')
        return False
    return True


@pytest.fixture(scope="session")
def http_service(check_option_with_docker, docker_ip, docker_services, docker_cleanup):
    """Ensure that HTTP service is up and responsive."""

    if not check_option_with_docker:
        return None

    #
    # print(docker_cleanup) # list with commands to run at the end
    # docker_cleanup = None

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("httpbin", 80)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_responsive(url))

    return url


@is_docker_available
@pytest.mark.with_docker
def test_status_code(check_option_with_docker, http_service):

    if not check_option_with_docker:
        return None

    status = 418
    response = requests.get(http_service + "/status/{}".format(status))

    assert response.status_code == status
