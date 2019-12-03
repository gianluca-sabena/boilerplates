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
import splitter

logger = common.get_logger()


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
    return args

def action_upload(args):
    splits = common.split_file_by_size(args.fs_path, args.tar_size)
    # Test s3 connection
    s3Manager = s3util.S3Manager(args)
    s3Manager.get_client()
    # Test write access to bucket
    # s3Manager.bucket_exsist(args.s3_bucket)
    s3Manager.bucket_create(args.s3_bucket)
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
        future_split = {executor.submit(splitter.Splitter, event, args, stats, split): split for split in splits}
        #for split in splitter:

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
    main(sys.argv[1:])

#
# --- main --- --- --- ---
#
def main(sys_args):
    try:
        args = cli(sys_args)
        if args.action == "upload":
            action_upload(args)
    except ValueError as ex:
        logger.error(f"ValueError: {ex}")
        raise ValueError(ex)
        #exit(1)


if __name__ == '__main__':
    run_cli()
