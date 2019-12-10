"""S3 utility: connection manager, s3 url"""
import os
import threading
import json
import time
import re
import boto3
import boto3.session
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
import urllib3
import s3split.common

# logger = s3split.common.get_logger()
urllib3.disable_warnings()

# From https://github.com/s3tools/s3cmd/blob/master/S3/S3Uri.py


class S3Uri():
    """Contain a s3 url s3://bucket/object"""
    _re = re.compile("^s3:///*([^/]*)/?(.*)", re.IGNORECASE | re.UNICODE)

    def __init__(self, string):
        self.bucket = None
        self.object = None
        match = self._re.match(string)
        if not match:
            raise ValueError("%s: not a S3 URI" % string)
        groups = match.groups()
        # if len(match.groups) == 0
        self.bucket = groups[0]
        self.object = groups[1]


class Stats():
    """Global stats ovject, updated from different working threads"""

    def __init__(self, interval):
        self._logger = s3split.common.get_logger()
        self._interval = interval
        self._stats = {}
        self._byte_sent = 0
        self._update_count = 0
        self._time_start = time.time()
        self._time_update = 0
        self._time_print_stat = time.time()
        self._lock = threading.Lock()

    def _add(self, file):
        with self._lock:
            self._stats[file] = {'size': float(os.path.getsize(file)), 'transferred': 0, 'completed': False}

    def print(self):
        """print stats with logger"""
        completed = 0
        total = 0
        elapsed_time = time.time() - self._time_start
        mb_sent = self._byte_sent / 1024 / 1024
        msg = ""
        for file in self._stats:
            total += 1
            stat = self._stats[file]
            if stat['completed'] is True:
                completed += 1
            else:
                percentage = (stat['transferred'] / stat['size']) * 100
                msg += f" - {file} ({percentage}%)\n"
        self._logger.info(
            f"\n --- stats ---\nElapsed time: {elapsed_time}\nMb sent: {mb_sent}\nTransfer rate: {(mb_sent)/elapsed_time} Mb/s\nFile completed: {completed}/{total}\nIn progress:\n{msg}")

    def _update(self, file, byte):
        with self._lock:
            self._time_update = time.time()
            self._stats[file]['transferred'] += byte
            self._byte_sent += byte
            if self._stats[file]['transferred'] == self._stats[file]['size']:
                self._stats[file]['completed'] = True
            self._update_count += 1
            if time.time() - self._time_print_stat > self._interval:
                self._time_print_stat = time.time()
                self.print()


class ProgressPercentage(object):
    """progress upload callback from boto3"""
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
    """Manage S3 connection with boto3"""

    def __init__(self, s3_access_key, s3_secret_key, s3_endpoint, s3_use_ssl, s3_bucket, s3_path, stats):
        self._logger = s3split.common.get_logger()
        self._stats = stats
        self._session = boto3.session.Session()
        self.s3_bucket = s3_bucket
        self.s3_path = s3_path
        #self.fs_path = fs_path
        self._s3_client = None
        # create client from session (thread safe)
        try:
            # TODO: detect ssl from endpoint true if start with https:
            # TODO: pass verify form command line argument
            self._s3_client = self._session.client('s3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key,
                                                   endpoint_url=s3_endpoint, use_ssl=s3_use_ssl, verify=False,
                                                   config=botocore.config.Config(max_pool_connections=25))
        except ValueError as ex:
            raise ValueError(f"S3 ValueError: {ex}")
        except ClientError as ex:
            raise ValueError(f"S3 ClientError: {ex}")

    def get_client(self):
        """return a oto3 client"""
        return self._s3_client

    def bucket_create(self, bucket):
        """create a bucket"""
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
        # Check if a bucket exsists
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html?highlight=clienterror#accessing-a-bucket
        try:
            self._s3_client.head_bucket(Bucket=bucket)
        except ValueError as ex:
            raise ValueError(f"S3 ValueError: {ex}")
        except ClientError as ex:

            # If it was a 404 error, then the bucket does not exist.
            if ex.response['Error']['Code'] == '404':
                return False
            else:
                self._logger.error(ex, ex.response)
                raise ValueError(f"S3 ClientError: {ex}")
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
        except ClientError as ex:
            # AllAccessDisabled error == bucket not found
            self._logger.error(ex)
            return None
        # Only return the contents if we found some keys
        if response['KeyCount'] > 0:
            return response['Contents']

        return None

    def upload_metadata(self, splits):
        """upload metadata file in json format"""
        content = {
            "info": {
                "hostname": "",
                "uname": "",
                "env": ""
            },
            "splits": splits}
        try:
            self._s3_client.put_object(Bucket=self.s3_bucket, Key=self.s3_path+'/s3split-metadata.json', Body=json.dumps(content))
        except ClientError as ex:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            self._logger.error(ex)
            return False
        return True

    def download_metadata(self):
        """download metadata and parse json"""
        try:
            self._logger.info(f"{self.s3_path+'/s3split-metadata.json'}")
            stream = self._s3_client.get_object(Bucket=self.s3_bucket, Key=self.s3_path+'/s3split-metadata.json')
            if stream is not None:
                data = stream['Body'].read().decode('utf-8')
                metadata = json.loads(data)
        except ClientError as ex:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            self._logger.error(ex)
            return None
        return metadata

    def upload_file(self, fs_path):
        """upload a single file with multiple parallel (concurrency) worlkers"""
        config = TransferConfig(multipart_threshold=1024 * 1024 * 64, max_concurrency=15,
                                multipart_chunksize=1024 * 1024 * 64, use_threads=True)
        final_path = self.s3_path+'/'+os.path.basename(fs_path)
        progress = ProgressPercentage(self._stats, fs_path)
        self._s3_client.upload_file(fs_path, self.s3_bucket, final_path,
                                    Config=config,
                                    Callback=progress
                                    )
