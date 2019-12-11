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

    def _add(self, file):
        with self._lock:
            self._stats[file] = {'size': float(os.path.getsize(file)), 'transferred': 0, 'completed': False}

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


class Action():
    """manage actions"""

    def __init__(self, args):
        self._args = args
        self._event = threading.Event()
        self._logger = s3split.common.get_logger()
        self._stats = Stats()
        self._executor = None
        # Validate
        if self._args.source is not None and not os.path.isdir(self._args.source):
            raise ValueError(f"source: '{self._args.source}' is not a directory")
        # Validate
        self._s3uri = s3split.s3util.S3Uri(self._args.target)
        self._s3_manager = s3split.s3util.S3Manager(self._args.s3_access_key, self._args.s3_secret_key, self._args.s3_endpoint,
                                                    self._args.s3_use_ssl, self._s3uri.bucket, self._s3uri.object, self._stats)
        # check S3 connection with dedicate method
        self._s3_manager.bucket_exsist()

    def stop(self):
        """stop processing"""
        self._event.set()
        if self._executor is not None:
            self._executor.shutdown()
        return True

    def check(self):
        """download splits to s3"""
        objects = self._s3_manager.list_bucket_objects()
        metadata = self._s3_manager.download_metadata()
        tar_data = {tar['name']: tar['size'] for tar in metadata["tars"]}
        s3_data = {obj['Key']: obj['Size'] for obj in objects}
        # LOGGER.info(pformat(objects))
        # LOGGER.info(pformat(metadata))
        # LOGGER.info(pformat(tar_data))
        # LOGGER.info(pformat(s3_data))
        errors = False
        if len(metadata["splits"]) != len(metadata["tars"]):
            self._logger.error("Number of slplits and tar files is different! Incomplete upload!")
            errors = True
        for key, val in tar_data.items():
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
        # objects = s3_manager.list_bucket_objects()
        # if objects is not None and len(objects) > 0:
        #     logger.warning(f"Remote S3 bucket is not empty!!!!!")
        #     metadata = s3_manager.download_metadata()
        #     if metadata is not None and len(metadata.get('splits')) > 0:
        #         if self._args.recovery is True:
        #             logger.warning(("Remote S3 bucket contain a metadata file "
        #                             "and --recovery parameter is set, recovery upload from remote metadata files"))
        #             # To do
        #         else:
        #             logger.warning("Remote S3 bucket contain a metadata file!!!! Use --recovery parameter to recovery upload or delete bucket")
        #             raise ValueError("Remote S3 bucket contain a metadata file")

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
                                                     self._args.s3_use_ssl, self._s3uri.bucket, self._s3uri.object, self._stats)
                splitter = s3split.splitter.Splitter(self._event, s3manager, self._args.source, split)
                future = executor.submit(splitter.run)
                future_split.update({future: split.get('id')})
            self._logger.debug(f"List of futures: {future_split}")
            for future in concurrent.futures.as_completed(future_split):
                try:
                    data = future.result()
                    tars_uploaded.append(data)
                except Exception as exc:  # pylint: disable=broad-except
                    self._logger.error(f"generated an exception: {exc}")
                    traceback_str = traceback.format_exc(exc)
                    self._logger.error(f"generated an exception: {traceback_str}")
                else:
                    self._logger.info(f"Split: {data['id']} Completed task processing")
        self._logger.debug(f"Tars uploaded completed - tars: {tars_uploaded}")
        if not self._s3_manager.upload_metadata(splits, tars_uploaded):
            self._logger.error("Metadata json file upload failed!")
            raise SystemExit
        self._stats.print()

