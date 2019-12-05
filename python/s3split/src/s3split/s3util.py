
import os
import boto3
import boto3.session
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
import urllib3
import threading

import s3split.common

logger = s3split.common.get_logger()
urllib3.disable_warnings()


class ProgressPercentage(object):
    files = dict()

    def __init__(self, stats, filename):
        self._filename = filename
        self._stats = stats
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        stats._add(filename)
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            self._stats._update(self._filename, bytes_amount)


class S3Manager():

    def __init__(self, s3_access_key, s3_secret_key, s3_endpoint, s3_use_ssl, s3_bucket, s3_path, stats):
        self._stats = stats
        self._session = boto3.session.Session()
        self.s3_bucket = s3_bucket
        self.s3_path = s3_path
        #self.fs_path = fs_path
        self._s3_client = None
        # create client from session (thread safe)
        try:
            self._s3_client = self._session.client('s3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key,
                                                   endpoint_url=s3_endpoint, use_ssl=s3_use_ssl, verify=False, config=botocore.config.Config(max_pool_connections=25))
        except ValueError as ex:
            raise ValueError(f"S3 ValueError: {ex}")
        except ClientError as ex:
            raise ValueError(f"S3 ClientError: {ex}")

    def get_client(self):
        return self._s3_client

    def bucket_create(self, bucket):
        if not self.bucket_exsist(bucket):
            try:
                self._s3_client.create_bucket(Bucket=bucket)
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'InvalidBucketName':
                    raise ValueError(f"S3 ClientError: {ex}")
                else:
                    return False
            else:
                return True

    def bucket_exsist(self, bucket):
        """Check if S3 bucket exsist

        :param bucket_name: Bucket to create
        :return: True if bucket is present, else False
        """

        # Check if a bucket exsists https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html?highlight=clienterror#accessing-a-bucket
        try:
            self._s3_client.head_bucket(Bucket=bucket)
        except ValueError as e:
            raise ValueError(f"S3 ValueError: {e}")
        except ClientError as e:

            # If it was a 404 error, then the bucket does not exist.
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(e, e.response)
                raise ValueError(f"S3 ClientError: {e}")
        else:
            return True

    def list_bucket_objects(self):
        """List the objects in an Amazon S3 bucket

        :param bucket_name: string
        :return: List of bucket objects. If error, return None.
        """

        # Retrieve the list of bucket objects
        try:
            response = self._s3_client.list_objects_v2(Bucket=self.s3_bucket)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            logger.error(e)
            return None
        logger.info("List bucket response:",response)
        # Only return the contents if we found some keys
        if response['KeyCount'] > 0:
            return response['Contents']

        return None

    def upload_file(self, fs_path, bucket, s3_path):
        config = TransferConfig(multipart_threshold=1024 * 1024 * 64, max_concurrency=15,
                                multipart_chunksize=1024 * 1024 * 64, use_threads=True)
        progress = ProgressPercentage(self._stats, fs_path)
        self._s3_client.upload_file(fs_path, bucket, s3_path,
                                    Config=config,
                                    Callback=progress
                                    )
