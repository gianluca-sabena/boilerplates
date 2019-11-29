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

import src.s3split.s3util 
import src.s3split.common

logger = src.s3split.common.get_logger()


class Stats():
    def __init__(self, interval):
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
        completed = 0
        total = 0
        elapsed_time = time.time() - self._time_start
        mb_sent = self._byte_sent / 1024 / 1024
        msg = ""
        for f in self._stats:
            total += 1
            s = self._stats[f]
            if s['completed'] is True:
                completed += 1
            else:
                percentage = (s['transferred'] / s['size']) * 100
                msg += f" - {f} ({percentage}%)\n"
        logger.info(f"\n --- stats ---\nElapsed time: {elapsed_time}\nMb sent: {mb_sent}\nTransfer rate: {(mb_sent)/elapsed_time} Mb/s\nFile completed: {completed}/{total}\nIn progress:\n{msg}")

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
            if self.mk_bucket() is True:
                self.processing()
            else:
                logger.error("Can not create bucket: "+self.bucket)
        else:
            logger.debug(f"Split: {split.get('id')} - Create Splitter class skipped because terminating event is set")

    # def _stats(self, bytes_amount):
    #     self._stat_byte_sent += bytes_amount

    def mk_bucket(self):
        """Create an S3 bucket in a specified region

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """

        # Check if a bucket exsists https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html?highlight=clienterror#accessing-a-bucket
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            if e.response['Error']['Code'] == '404':
                # Create bucket
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket)
                except ClientError as e:
                    logger.error(e, e.response)
                    return False
                return True
            # elif e.response['Error']['Code'] == '404':
            #     logger.error("User has no access to bucket")
            #     # exit(404)
            else:
                logger.error(e, e.response)
                return False
        return True

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


def cli(args):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, prog='s3split',
                                     description='A python utility to tar and upload a group of objects (files or folders) to S3 endpoint')
    parser.add_argument('--s3-secret-key', help='S3 secret key', required=True, default="")
    parser.add_argument('--s3-access-key', help='S3 access key', required=True, default="")
    parser.add_argument('--s3-endpoint', help='S3 endpoint full hostname in the form http://myhost:port', required=True, default="")
    parser.add_argument('--s3-use-ssl', help='S3 endpoint ssl', required=False, default=False)
    parser.add_argument('--s3-bucket', help='S3 target bucket', required=True, default="")
    parser.add_argument('--s3-path', help='S3 target path', required=False, default="s3split")
    parser.add_argument('--fs-path', help='Local filesystem path to upload revursively', required=True, default="")
    parser.add_argument('--tar-size', help='Max size in MB for a single split tar file', required=False, type=int, default=500)
    parser.add_argument('--threads', help='Number of parallel threads ', required=False, type=int, default=5)
    parser.add_argument('--stats-interval', help='Seconds between two stats print', required=False, type=int, default=5)
    parser.add_argument('action', choices=['upload', 'download', 'check'])
    args = parser.parse_args(args)
    logger.info(f"S3 target: {args.s3_endpoint}/{args.s3_bucket}/{args.s3_path}")
    logger.info(f"Filesystem path: {args.fs_path}")
    logger.info(f"Parallel threads (split/tar files): {args.threads}")
    logger.info(f"Stats interval print: {args.stats_interval} seconds")
    # Start validation
    if not os.path.isdir(args.fs_path):
        logger.error(f"--fs-path argument is not a valid directory")
        raise SystemExit("args validation error fs path")
    # Test s3 connection
    s3Manager = src.s3split.s3util.S3Manager(args)
    s3Manager.get_client()
    return args


def main(args):
    try:
        args = cli(args)
        splits = src.s3split.common.split_file_by_size(args.fs_path, args.tar_size)
    except SystemExit:
        #logger.error(f"Exit due to a validation error - {ex}")
        exit(1)
    event = threading.Event()
    stats = Stats(args.stats_interval)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        def signal_handler(sig, frame):
            logger.info('You pressed Ctrl+C!... \n\nThe program will terminate AFTER ongoing file upload(s) complete\n\n')
            # Send termination signal to threads
            event.set()
            executor.shutdown()
        # Catch ctrl+c
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        # Start the load operations and mark each future with its URL
        future_split = {executor.submit(Splitter, event, args, stats, split): split for split in splits}
        for future in concurrent.futures.as_completed(future_split):
            future_split[future]
            try:
                data = future.result()
            except Exception as exc:
                logger.error(f"generated an exception: {exc}")
                traceback_str = traceback.format_exc(exc)
                logger.error(f"generated an exception: {traceback_str}")
            else:
                logger.info(f"Split: {data.split.get('id')} - Completed task processing")
    # logger.info(f"Debug stats: {stats._stats}")
    stats.print()

def run_cli():
    """entry point for setup.py console script"""
    main(sys.argv)

if __name__ == '__main__':
    run_cli()
