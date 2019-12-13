# pylint: disable=missing-function-docstring,unused-argument,redefined-outer-name
"""test"""
import os
from pprint import pformat
import pytest
import docker
import s3split.common
import s3split.main
import s3split.s3util
import common

DOCKER_MINIO_IMAGE = "minio/minio:RELEASE.2019-10-12T01-39-57Z"
MINIO_ACCESS_KEY = "test_access"
MINIO_SECRET_KEY = "test_secret"
MINIO_ENDPOINT = "http://127.0.0.1:9000"
MINIO_USE_SSL = False
MINIO_BUCKET = "s3split"
MINIO_PATH = "test"

LOGGER = s3split.common.get_logger()


@pytest.fixture(scope="module")
def docker_minio_fixture():
    """start docker container with minio"""
    # TODO: add a check to pull image if not present
    client = docker.from_env()
    # Check if minio is running
    LOGGER.info("--- docker_minio_fixture")
    try:
        minio = client.containers.get('minio')
    except docker.errors.NotFound:
        LOGGER.info("Container minio not found... creating...")
        minio = client.containers.create(DOCKER_MINIO_IMAGE, 'server /tmp', ports={'9000/tcp': 9000}, detach=True, name="minio",
                                         environment={"MINIO_ACCESS_KEY": MINIO_ACCESS_KEY, "MINIO_SECRET_KEY": MINIO_SECRET_KEY})
    if minio.status != 'running':
        LOGGER.info("Container minio not running... starting...")
        minio.start()
    return True





@pytest.mark.args
def test_minio_invalid_s3uri(docker_minio_fixture):
    """test minio connection error"""
    with pytest.raises(SystemExit, match=r'S3 URI must contains bucket and path s3://bucket/path'):
        assert s3split.main.run_main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "upload", "/tmp", "s3://aaa"])


@pytest.mark.args
def test_argparse_invalid_local_path(docker_minio_fixture):
    """test that exception is raised for invalid local path"""
    with pytest.raises(ValueError, match=r"source: 'D' is not a directory"):
        assert s3split.main.run_main(["--s3-secret-key", "A", "--s3-access-key", "B", "--s3-endpoint", "C", "upload", "D", "s3://aaa/bbb"])


@pytest.mark.args
def test_minio_invalid_endpoint(docker_minio_fixture):
    """test minio connection error"""
    with pytest.raises(ValueError, match=r"S3 ValueError: Invalid endpoint: C"):
        assert s3split.main.run_main(["--s3-secret-key", "A", "--s3-access-key", "B",
                                      "--s3-endpoint", "C", "upload", "/tmp", "s3://aaa/bbb"])


@pytest.mark.args
def test_minio_invalid_bucket(docker_minio_fixture):
    n_files = 100
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    common.generate_random_files(full_path, n_files, size)
    with pytest.raises(SystemExit, match=r'S3 URI must contains bucket and path s3://bucket/path'):
        assert s3split.main.run_main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY,
                                      "--s3-endpoint", MINIO_ENDPOINT, "upload", full_path, "s3://ddd/"])


@pytest.mark.full
def test_minio_upload(docker_minio_fixture):
    n_files = 200
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    common.generate_random_files(full_path, n_files, size)
    s3split.main.run_main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT,
                           "--threads", "2", "--stats-interval", "1", "upload", full_path, f"s3://{MINIO_BUCKET}/{MINIO_PATH}",
                           "--tar-size", "10", "--recovery", "true"])
    s3split.main.run_main(["--s3-secret-key", MINIO_SECRET_KEY, "--s3-access-key", MINIO_ACCESS_KEY, "--s3-endpoint", MINIO_ENDPOINT,
                           "check", full_path, f"s3://{MINIO_BUCKET}/{MINIO_PATH}"])

    # download metadata
    # stats = s3split.s3util.Stats(1)
    # s3_manager = s3split.s3util.S3Manager(MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT,
    #                                       MINIO_USE_SSL, MINIO_BUCKET, MINIO_PATH, stats)
    # objects = s3_manager.list_bucket_objects()
    # metadata = s3_manager.download_metadata()
    # tar_data = {tar['name']: tar['size'] for tar in metadata["tars"]}
    # s3_data = {obj['Key']: obj['Size'] for obj in objects}
    # LOGGER.info(pformat(objects))
    # LOGGER.info(pformat(metadata))
    # LOGGER.info(pformat(tar_data))
    # LOGGER.info(pformat(s3_data))
    # if len(metadata["splits"]) != len(metadata["tars"]):
    #     LOGGER.error("Number of sllits and tar files is different! Incomplete upload!")
    # for key, val in tar_data.items():
    #     if s3_data.get(key) is None:
    #         LOGGER.error(f"Split part {key} not found on S3! Inclomplete uploads detected!")
    #     elif s3_data.get(key) == val:
    #         LOGGER.info(f"Check size for split part {key}: OK")
    #     elif s3_data.get(key) != val:
    #         LOGGER.error((f"Check size for split part {key} failed! "
    #                        "Expected size: {val} comparade to s3 object size: {s3_data.get('key')} "))


@pytest.mark.s3
def test_s3_list_bucket():
    "full s3 operation"
    # stats = s3split.actions.Stats(1)
    s3_manager = s3split.s3util.S3Manager(MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT,
                                          MINIO_USE_SSL, MINIO_BUCKET+'._!', MINIO_PATH+'._!')
    s3_manager.bucket_exsist()
    s3_manager.create_bucket()
    objects = s3_manager.list_bucket_objects()
    LOGGER.info(objects)


@pytest.mark.last
def test_s3_uri():
    s3_uri = s3split.s3util.S3Uri("s3://aaa/bbb")
    LOGGER.info(f"{s3_uri.bucket} {s3_uri.object}")
    test = s3_uri.bucket == "aaa" and s3_uri.object == "bbb"
    assert test


@pytest.mark.last
def test_s3_uri_missing_path():
    with pytest.raises(SystemExit, match=r'S3 URI must contains bucket and path s3://bucket/path'):
        assert s3split.s3util.S3Uri("s3://aaa")
