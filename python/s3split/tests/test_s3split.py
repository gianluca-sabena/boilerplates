# pylint: disable=missing-function-docstring,unused-argument,redefined-outer-name
"""test full application"""
from pprint import pformat
import pytest
import s3split.common
import s3split.main
import s3split.s3util
import common


LOGGER = s3split.common.get_logger()


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
        assert s3split.main.run_main(["--s3-secret-key", common.MINIO_SECRET_KEY, "--s3-access-key", common.MINIO_ACCESS_KEY,
                                      "--s3-endpoint", common.MINIO_ENDPOINT, "upload", full_path, "s3://ddd/"])


@pytest.mark.full
def test_minio_upload(docker_minio_fixture):
    n_files = 200
    size = 1024
    full_path = f"/tmp/s3split-pytest/{n_files}f-{size}kb"
    common.generate_random_files(full_path, n_files, size)
    s3split.main.run_main(["--s3-secret-key", common.MINIO_SECRET_KEY, "--s3-access-key", common.MINIO_ACCESS_KEY,
                           "--s3-endpoint", common.MINIO_ENDPOINT, "--threads", "2", "--stats-interval", "1",
                           "upload", full_path, f"s3://{common.MINIO_BUCKET}/{common.MINIO_PATH}", "--tar-size", "10"])
    s3split.main.run_main(["--s3-secret-key", common.MINIO_SECRET_KEY, "--s3-access-key", common.MINIO_ACCESS_KEY,
                           "--s3-endpoint", common.MINIO_ENDPOINT,
                           "check", f"s3://{common.MINIO_BUCKET}/{common.MINIO_PATH}"])

    # download metadata
    # stats = s3split.s3util.Stats(1)
    # s3_manager = s3split.s3util.S3Manager(common.MINIO_ACCESS_KEY, common.MINIO_SECRET_KEY, common.MINIO_ENDPOINT,
    #                                       common.MINIO_USE_SSL, common.MINIO_BUCKET, common.MINIO_PATH, stats)
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
