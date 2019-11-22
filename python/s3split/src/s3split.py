import sys
import argparse
import concurrent.futures
import logging
import queue
import random
import threading
import time
import traceback
import os
import boto3
import boto3.session
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
import urllib3
import signal

urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO)


def cli():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, prog='main.py',
                                     usage='%(prog)s [options]', description='A python utility to tar and upload a group of objects (files or folders) to S3 endpoint')
    parser.add_argument('--s3-secret-key', help='S3 secret key', required=True, default="")
    parser.add_argument('--s3-access-key', help='S3 access key', required=True, default="")
    parser.add_argument('--s3-endpoint', help='S3 endpoint full hostname in the form http://myhost:port', required=True, default="")
    parser.add_argument('--s3-use-ssl', help='S3 endpoint ssl', required=True, default=False)
    parser.add_argument('--s3-bucket', help='S3 target bucket', required=True, default="")
    parser.add_argument('--source-path', help='local filesystem path to process', required=True, default="")
    parser.add_argument('--objects', help='first level objects (file or folder) to put in a single split', required=False, default=2)
    parser.add_argument('--threads', help='Number of parallel threads ', required=False, default=10)
    args = parser.parse_args()
    return args


def get_file_list(path, split_size):
    splits = queue.Queue(maxsize=0)
    onlyfiles = [os.path.join(path, f) for f in sorted(os.listdir(path)) if os.path.isfile(os.path.join(path, f))]
    for n, i in enumerate(range(0, len(onlyfiles), split_size)):
        s = {'paths': onlyfiles[i:i + split_size], 'id': n+1}
        splits.put(s)
    return splits
    # for f in os.listdir(path):
    #     if os.path.isfile(os.path.join(path, f)):
    #         statinfo = os.stat(os.path.join(path, f))
    #         logging.info(statinfo)
    # logging.info(onlyfiles)


class Stats():
    def __init__(self):
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
        byte_sent = 0
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
        logging.info(f"\n --- stats ---\nElapsed time: {elapsed_time}\nMb sent: {mb_sent}\nTransfer rate: {(mb_sent)/elapsed_time} Mb/s\nFile completed: {completed}/{total}\nIn progress:\n{msg}")

    def _update(self, file, byte):
        with self._lock:
            self._time_update = time.time()
            self._stats[file]['transferred'] += byte
            self._byte_sent += byte
            if self._stats[file]['transferred'] == self._stats[file]['size']:
                self._stats[file]['completed'] = True
            self._update_count += 1
            if time.time() - self._time_print_stat > 10:
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
            logging.debug(f"Split: {split.get('id')} - Create Splitter class")
            self._stats = stats
            session = boto3.session.Session()
            try:
                self.client_config = botocore.config.Config(max_pool_connections=25)
                self.s3_client = session.client('s3', aws_access_key_id=args.s3_access_key, aws_secret_access_key=args.s3_secret_key,
                                                endpoint_url=args.s3_endpoint, use_ssl=args.s3_use_ssl, verify=False, config=self.client_config)
            except ClientError as e:
                logging.error(e)
            self.split = split
            self.bucket = args.s3_bucket
            self.mk_bucket()
            self.task()
        else:
            logging.debug(f"Split: {split.get('id')} - Create Splitter class skipped because terminating event is set")

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
                    logging.error(e)
                    return False
                return True
            # elif e.response['Error']['Code'] == '404':
            #     logging.error("User has no access to bucket")
            #     # exit(404)
            else:
                logging.error(e)
                return False

    def multi_part_upload(self, path):
        logging.info(f"Split: {self.split.get('id')} - Start upload path: {path}")
        config = TransferConfig(multipart_threshold=1024 * 1024 * 64, max_concurrency=15,
                                multipart_chunksize=1024 * 1024 * 64, use_threads=True)
        key_path = os.path.basename(path)
        progress = ProgressPercentage(self._stats, path)
        self.s3_client.upload_file(path, self.bucket, key_path,
                                   Config=config,
                                   Callback=progress
                                   )

    def task(self):
        logging.info(f"Split: {self.split.get('id')} - Start task processing")
        for p in self.split.get('paths'):
            if not event.is_set():
                self.multi_part_upload(p)
            else:
                logging.info(f"Split: {self.split.get('id')} - Download interrupted because terminating event is set!")


if __name__ == '__main__':
    args = cli()
    event = threading.Event()
    # logging.info(f"Cli args: {args}")
    stats = Stats()
    start_time = time.time()
    splits = get_file_list(args.source_path, args.objects)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        def signal_handler(sig, frame):
            logging.info('You pressed Ctrl+C!... \n\nThe program will terminate AFTER ongoing file upload(s) complete\n\n')
            # Send termination signal to threads
            event.set()
            executor.shutdown()
        # Catch ctrl+c
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        # Start the load operations and mark each future with its URL
        future_split = {executor.submit(Splitter, event, args, stats, split): split for split in splits.queue}
        for future in concurrent.futures.as_completed(future_split):
            f = future_split[future]
            try:
                data = future.result()
            except Exception as exc:
                logging.error(f"generated an exception: {exc}")
                traceback_str = traceback.format_exc(exc)
                logging.error(f"generated an exception: {traceback_str}")
            else:
                logging.info(f"Split: {data.split.get('id')} - Completed task processing")
    # logging.info(f"Debug stats: {stats._stats}")
    stats.print()
