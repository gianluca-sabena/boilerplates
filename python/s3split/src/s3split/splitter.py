import sys
import os
import argparse
import concurrent.futures
import threading
import time
import traceback

import signal
import tarfile
import tempfile
import pprint

import boto3
import boto3.session
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

import s3util
import common

logger = common.get_logger()
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


class Splitter():
    def __init__(self, event, args, stats, split):
        if not event.is_set():
            logger.debug(f"Split: {split.get('id')} - Create Splitter class")
            self._event = event
            self._args = args
            self._stats = stats
            self.split = split
            self.bucket = args.s3_bucket
            self.name_tar = f"s3cmd-split-{self.split.get('id')}.tar"
            session = boto3.session.Session()
            try:
                self.client_config = botocore.config.Config(max_pool_connections=25)
                self.s3_client = session.client('s3', aws_access_key_id=args.s3_access_key, aws_secret_access_key=args.s3_secret_key,
                                                endpoint_url=args.s3_endpoint, use_ssl=args.s3_use_ssl, verify=False, config=self.client_config)
            except ClientError as e:
                logger.error(e)
            self.processing()
            # if self.mk_bucket() is True:
            #     self.processing()
            # else:
            #     logger.error("Can not create bucket: "+self.bucket)
        else:
            logger.debug(f"Split: {split.get('id')} - Create Splitter class skipped because terminating event is set")

    # def _stats(self, bytes_amount):
    #     self._stat_byte_sent += bytes_amount

    
    def _multi_part_upload(self, path):
        if not self._event.is_set():
            logger.debug(f"Split: {self.split.get('id')} - Start upload path: {path}")
            config = TransferConfig(multipart_threshold=1024 * 1024 * 64, max_concurrency=15,
                                    multipart_chunksize=1024 * 1024 * 64, use_threads=True)
            progress = ProgressPercentage(self._stats, path)
            self.s3_client.upload_file(path, self.bucket, self._args.s3_path+'/'+os.path.basename(path),
                                       Config=config,
                                       Callback=progress
                                       )
        else:
            logger.info(f"Split: {self.split.get('id')} - Upload interrupted because terminating event is set!")

    def _tar(self):
        # Filter function to update tar path, required to untar in a safe location
        def filter(tobj):
            new = tobj.name.replace(self._args.fs_path.strip('/'), self._args.s3_path.strip('/'))
            # logger.debug(f"path: {self._args.fs_path} - {tobj.name} - {new}")
            tobj.name = new
            return tobj
        if not self._event.is_set():
            logger.debug(f"Split: {self.split.get('id')} - Start create tar {self.name_tar}")
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_file = os.path.join(tmpdir, self.name_tar)
                with tarfile.open(tar_file, "w") as tar:
                    for path in self.split.get('paths'):
                        # remove base path from folder with filter function
                        tar.add(path, filter=filter)
                logger.debug(f"Split: {self.split.get('id')} - Generated tar file {tar_file}")
                # Start upload
                self._multi_part_upload(tar_file)
        else:
            logger.info(f"Split: {self.split.get('id')} - Tar interrupted because terminating event is set!")

    def processing(self):
        logger.debug(f"Split: {self.split.get('id')} - Start processing")
        if not self._event.is_set():
            self._tar()
        else:
            logger.info(f"Split: {self.split.get('id')} - processing interrupted because terminating event is set!")
