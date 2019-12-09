import pytest
import logging
import os
from pprint import pformat
# pylint: disable=import-error
import s3split.common
import s3split.main
import s3split.s3util

logger = s3split.common.get_logger()

DOCKER_MINIO_IMAGE = "minio/minio:RELEASE.2019-10-12T01-39-57Z"
MINIO_ACCESS_KEY = "test_access"
MINIO_SECRET_KEY = "test_secret"
MINIO_ENDPOINT = "http://127.0.0.1:9000"
MINIO_USE_SSL = False
MINIO_BUCKET = "s3split"
MINIO_PATH = "test"


@pytest.fixture(scope="module")
def docker_minio_fixture():
    # TODO: add a check to pull image if not present
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
            fout.write(os.urandom(size * 1024))


def test_argparse_invalid_local_path(docker_minio_fixture):
    """test that exception is raised for invalid local path"""
    with pytest.raises(ValueError, match=r"--fs-path argument is not a valid directory"):
        assert s3split.main.run_main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--fs-path", "E", "upload"])


def test_minio_invalid_endpoint(docker_minio_fixture):
    """test minio connection error"""
    with pytest.raises(ValueError, match=r"S3 ValueError: Invalid endpoint: C"):
        assert s3split.main.run_main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "--s3-bucket", "D", "--fs-path", "/tmp", "upload"])


def test_minio_invalid_bucket(docker_minio_fixture):
    n_files = 100
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    generate_random_files(full_path, n_files, size)
    with pytest.raises(ValueError, match=r'S3 ClientError: An error occurred \(InvalidBucketName\).*'):
        assert s3split.main.run_main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT, "--s3-bucket", "D", "--fs-path", full_path, "upload"])


def test_minio_upload(docker_minio_fixture):
    n_files = 100
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    generate_random_files(full_path, n_files, size)
    s3split.main.run_main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT,
                           "--s3-bucket", MINIO_BUCKET, "--s3-path", MINIO_PATH, "upload", "--fs-path", full_path, "--tar-size", "10"])
    # download metadata
    stats = s3split.main.Stats(1)
    s3 = s3split.s3util.S3Manager(MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT, MINIO_USE_SSL, MINIO_BUCKET, MINIO_PATH, stats)
    objects = s3.list_bucket_objects()
    logger.info(pformat(objects))
    metadata = s3.download_metadata()
    logger.info(pformat(metadata))


def NO_test_s3_list_bucket():
    stats = s3split.main.Stats(1)
    s3 = s3split.s3util.S3Manager(MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT, MINIO_USE_SSL, MINIO_BUCKET, MINIO_PATH, stats)
    objects = s3.list_bucket_objects()
    logger.info(objects)
