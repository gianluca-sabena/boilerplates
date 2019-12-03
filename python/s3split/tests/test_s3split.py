import pytest
import logging
import os
import pprint

import common # pylint: disable=import-error
import main # pylint: disable=import-error

logger = common.get_logger()

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

def generate_random_files(full_path, n_files, size):
    """path, n_files, number of files file size in kb"""
    if not os.path.isdir(full_path):
        try:
            os.makedirs(full_path)
        except OSError as ex:
            logger.error(f"Creation of the directory {full_path} failed - {ex}")
        else:
            logger.info(f"Successfully created the directory {full_path}")
    for i in range(n_files):
        with open(os.path.join(full_path, f"file_{i+1}.txt"), 'wb') as fout:
            fout.write(os.urandom(1024))


def test_argparse_invalid_local_path(docker_minio_fixture):
    """test that exception is raised for invalid local path"""
    with pytest.raises(ValueError, match=r"--fs-path argument is not a valid directory"):
        assert main.main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--fs-path", "E", "upload"])


def test_minio_invalid_endpoint(docker_minio_fixture):
    """test minio connection error"""
    with pytest.raises(ValueError, match=r"S3 ValueError: Invalid endpoint: C"):
        assert main.main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--fs-path", "/tmp", "upload"])


def test_minio_connection_success(docker_minio_fixture):
    """test minio connecction ok"""
    args = main.cli(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT, "--s3-bucket", "D", "--fs-path", "/tmp", "upload"])
    logger.info(pprint.pprint(args))


def test_minio_invalid_bucket(docker_minio_fixture):
    n_files= 10
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    generate_random_files(full_path, n_files, size)
    with pytest.raises(ValueError, match=r'S3 ClientError: An error occurred \(InvalidBucketName\).*'):
        assert main.main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT, "--s3-bucket", "D", "--fs-path", full_path, "upload"])

def test_minio_upload(docker_minio_fixture):
    n_files= 10
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    generate_random_files(full_path, n_files, size)
    main.main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT, "--s3-bucket", "test", "--fs-path", full_path, "upload"])