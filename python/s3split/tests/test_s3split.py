import pytest
import logging

import src.s3split.common
from src.s3split.main import cli

logger = src.s3split.common.get_logger()

DOCKER_MINIO_IMAGE = "minio/minio:RELEASE.2019-10-12T01-39-57Z"
MINIO_ACCESS_KEY = "test_access"
MINIO_SECRET_KEY = "test_secret"
MINIO_ENDPOINT = "http://127.0.0.1:9000"


@pytest.fixture(scope="module")
def docker_minio_fixture():
    import docker
    client = docker.from_env()
    # Check if minio is running
    logger.info("--- docker_minio_fixture")
    try:
        minio = client.containers.get('minio')
    except docker.errors.NotFound:
        logger.info("Container minio not found... creating...")
        minio = client.containers.create(DOCKER_MINIO_IMAGE, 'server /tmp', ports={'9000/tcp': 9000}, detach=True, name="minio",
                                         environment={"MINIO_ACCESS_KEY": MINIO_ACCESS_KEY, "MINIO_SECRET_KEY": MINIO_SECRET_KEY})
    if minio.status != 'running':
        logger.info("Container minio not running... starting...")
        minio.start()
    return True


def func(x):
    return x + 1


def test_answer(docker_minio_fixture):
    assert func(3) == 4


def test_argparse_invalid_local_path(docker_minio_fixture):
    """test that exception is raised for invalid local path"""
    with pytest.raises(SystemExit, match=r"args validation error fs path"):
        out = cli(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--fs-path", "E", "upload"])
        assert out


def test_minio_connection_error(docker_minio_fixture):
    """test minio connection error"""
    # captured = capsys.readouterr()
    print("XXXXXX")
    with pytest.raises(SystemExit, match=r"args validation error S3 endpoint") as excinfo:
        cli(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--fs-path", "/tmp", "upload"])
        assert "maximum recursion" in str(excinfo.value)


def test_minio_connection_success(docker_minio_fixture):
    """test minio connecction ok"""
    cli(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT, "--s3-bucket", "D", "--fs-path", "/tmp", "upload"])
