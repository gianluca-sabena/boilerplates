"""main actions: upload, check"""
import os
import time
import threading
import traceback
import concurrent.futures

import s3split.s3util
import s3split.common
import s3split.splitter

class Stats():
    """Global stats ovject, updated from different working threads"""

    def __init__(self, interval=30):
        self._logger = s3split.common.get_logger()
        self._interval = interval
        self._stats = {}
        self._byte_sent = 0
        self._update_count = 0
        self._time_start = time.time()
        self._time_update = 0
        self._time_print_stat = time.time()
        self._lock = threading.Lock()

    # def _add(self, file):
    #     with self._lock:
    #         self._stats[file] = {'size': float(os.path.getsize(file)), 'transferred': 0, 'completed': False}

    def print(self):
        """print stats with logger"""
        completed = 0
        total = 0
        elapsed_time = round(time.time() - self._time_start, 1)
        mb_sent = round(self._byte_sent / 1024 / 1024, 1)
        rate = round((mb_sent)/elapsed_time, 1)
        msg = ""
        for file in self._stats:
            total += 1
            stat = self._stats[file]
            if stat['completed'] is True:
                completed += 1
            else:
                percentage = round((stat['transferred'] / stat['size']) * 100, 1)
                msg += f" - {file} ({percentage}%)\n"
        txt = (f"\n --- stats ---\nElapsed time: {elapsed_time} seconds\n"
               f"Data sent: {mb_sent} Mb\nTransfer rate: {rate} Mb/s\n"
               f"File completed: {completed}/{total}")
        if len(msg) > 0:
            txt += f"\nUpload(s) in progress:\n{msg}"
        self._logger.info(txt)

    def update(self, file, byte, total_size):
        """update byte sent for a file"""
        with self._lock:
            # add new file
            if self._stats.get(file) is None:
                self._stats[file] = {'size': total_size, 'transferred': 0, 'completed': False}
            self._stats[file]['transferred'] += byte
            self._byte_sent += byte
            if self._stats[file]['transferred'] == self._stats[file]['size']:
                self._stats[file]['completed'] = True
            self._update_count += 1
            if time.time() - self._time_print_stat > self._interval:
                self._time_print_stat = time.time()
                self.print()


class Action():
    """manage actions"""

    def __init__(self, args):
        self._args = args
        self._event = threading.Event()
        self._logger = s3split.common.get_logger()
        self._stats = Stats(args.stats_interval)
        self._executor = None
        # Validate

        # Validate
        if args.action == "upload":
            self._s3uri = s3split.s3util.S3Uri(self._args.target)
            if not os.path.isdir(self._args.source):
                raise ValueError(f"upload source: '{self._args.source}' is not a directory")
            self._fsuri = self._args.source
        elif args.action == "download":
            self._s3uri = s3split.s3util.S3Uri(self._args.source)
            if os.path.isdir(self._args.target):
                raise ValueError(f"download target directory '{self._args.target}' exsists... Please provide a new path!")
            self._fsuri = self._args.target
        elif args.action == "check":
            self._s3uri = s3split.s3util.S3Uri(self._args.target)
            self._fsuri = None

        self._s3_manager = s3split.s3util.S3Manager(self._args.s3_access_key, self._args.s3_secret_key, self._args.s3_endpoint,
                                                    self._args.s3_verify_ssl, self._s3uri.bucket, self._s3uri.object, self._stats.update)
        # check S3 connection with dedicate method
        self._s3_manager.bucket_exsist()

    def stop(self):
        """stop processing"""
        self._event.set()
        if self._executor is not None:
            self._executor.shutdown()
        return True

    def download(self):
        "download files from s3"
        def downloader(s3manager, s3_obj, s3_size):
            self._logger.info(f"Start download in a thread for file: {s3_obj}")
            return s3manager.download_file(s3_obj, s3_size, os.path.join(self._fsuri, s3_obj))

        metadata = self._s3_manager.download_metadata()
        # from pprint import pformat
        # self._logger.info(pformat(metadata))
        if not os.path.isdir(self._fsuri):
            try:
                os.makedirs(self._fsuri)
            except OSError as ex:
                raise SystemExit(f"Creation of the directory {self._fsuri} failed - {ex}")
            else:
                self._logger.info(f"Successfully created download directory {self._fsuri}")
        futures = {}
        downloaded = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._args.threads) as executor:
            for s3_obj in metadata["tars"]:
                self._logger.info(f"Downloading {s3_obj['name']}")
                s3manager = s3split.s3util.S3Manager(self._args.s3_access_key, self._args.s3_secret_key, self._args.s3_endpoint,
                                                    self._args.s3_verify_ssl, self._s3uri.bucket, self._s3uri.object, self._stats.update)
                future = executor.submit(downloader, s3manager, s3_obj['name'], s3_obj['size'])
                futures.update({future: s3_obj['name']})
            self._logger.debug(f"List of futures: {futures}")
            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    downloaded.append(data)
                except Exception as exc:  # pylint: disable=broad-except
                    self._logger.error(f"Thread generated an exception: {exc}")
                    traceback_str = traceback.format_exc(exc)
                    self._logger.error(f"Thread generated an exception: {traceback_str}")
                else:
                    self._logger.info(f"Download completed {data}")
        self._stats.print()




    def check(self):
        """download splits to s3"""
        metadata = self._s3_manager.download_metadata()
        tar_metadata = {tar['name']: tar['size'] for tar in metadata["tars"]}
        objects = self._s3_manager.list_bucket_objects()
        s3_data = {obj['Key']: obj['Size'] for obj in objects}
        errors = False
        if len(metadata["splits"]) != len(metadata["tars"]):
            self._logger.error("Number of slplits and tar files is different! Incomplete upload!")
            errors = True
        for key, val in tar_metadata.items():
            key = os.path.join(self._s3uri.object, key)
            if s3_data.get(key) is None:
                self._logger.error(f"Split part {key} not found on S3! Inclomplete uploads detected!")
                errors = True
            elif s3_data.get(key) == val:
                self._logger.info(f"Check size for split part {key}: OK")
            elif s3_data.get(key) != val:
                self._logger.error(
                    f"Check size for split part {key} failed! Expected size: {val} comparade to s3 object size: {s3_data.get('key')} ")
                errors = True
        return not errors

    def upload(self):
        """upload splits to s3"""
        self._logger.info(f"Tar object max size: {self._args.tar_size} MB")
        self._logger.info(f"Upload started! Print stats evry: {self._args.stats_interval} seconds")
        # Check if bucket is empty and if a metadata file is present
        objects = self._s3_manager.list_bucket_objects()
        if objects is not None and len(objects) > 0:
            self._logger.warning(f"Remote S3 bucket is not empty!!!!!")
            metadata = self._s3_manager.download_metadata()
            if metadata is not None and len(metadata.get('splits')) > 0:
                self._logger.warning("Remote S3 bucket contains a metadata file!")
                # TODO: If there is a remote metadata? exit and force user to clean bucket?
        # Upload metadata file
        splits = s3split.common.split_file_by_size(self._args.source, self._args.tar_size)
        tars_uploaded = []
        future_split = {}
        if not self._s3_manager.upload_metadata(splits):
            self._logger.error("Metadata json file upload failed!")
            raise SystemExit
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._args.threads) as executor:
            for split in splits:
                s3manager = s3split.s3util.S3Manager(self._args.s3_access_key, self._args.s3_secret_key, self._args.s3_endpoint,
                                                     self._args.s3_verify_ssl, self._s3uri.bucket, self._s3uri.object, self._stats.update)
                splitter = s3split.splitter.Splitter(self._event, s3manager, self._args.source, split)
                future = executor.submit(splitter.run)
                future_split.update({future: split.get('id')})
            self._logger.debug(f"List of futures: {future_split}")
            for future in concurrent.futures.as_completed(future_split):
                try:
                    data = future.result()
                    tars_uploaded.append(data)
                except Exception as exc:  # pylint: disable=broad-except
                    self._logger.error(f"Thread generated an exception: {exc}")
                    traceback_str = traceback.format_exc(exc)
                    self._logger.error(f"Thread generated an exception: {traceback_str}")
                else:
                    self._logger.info(f"Split: {data['id']} Completed task processing")
        self._logger.debug(f"Tars uploaded completed - tars: {tars_uploaded}")
        if not self._s3_manager.upload_metadata(splits, tars_uploaded):
            raise SystemExit("Metadata json file upload failed!")
        self._stats.print()
