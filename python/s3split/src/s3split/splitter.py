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



class Splitter():
    def __init__(self, event, s3manager, split):
        if not event.is_set():
            logger.debug(f"Split: {split.get('id')} - Create Splitter class for split: {split}")
            self._s3manager = s3manager
            self._event = event
            # self._args = args
            self._fs_path = s3manager.fs_path
            self._s3_bucket = s3manager.s3_bucket
            self._s3_path = s3manager.s3_path
            self.split = split
            # self.bucket = args.s3_bucket
            self.name_tar = f"s3cmd-split-{self.split.get('id')}.tar"
            self.processing()
        else:
            logger.debug(f"Split: {split.get('id')} - Create Splitter class skipped because terminating event is set")


    def _tar(self):
        # Filter function to update tar path, required to untar in a safe location
        def filter(tobj):
            new = tobj.name.replace(self._fs_path.strip('/'), self._s3_path.strip('/'))
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
                    if not self._event.is_set():
                        self._s3manager.upload_file(tar_file, self._s3_bucket, self._s3_path+'/'+os.path.basename(tar_file))
                    else:
                        logger.info(f"Split: {self.split.get('id')} - Upload interrupted because terminating event is set!")
        else:
            logger.info(f"Split: {self.split.get('id')} - Tar interrupted because terminating event is set!")

    def processing(self):
        logger.debug(f"Split: {self.split.get('id')} - Start processing")
        if not self._event.is_set():
            self._tar()
        else:
            logger.info(f"Split: {self.split.get('id')} - processing interrupted because terminating event is set!")
