"""Split files in tar"""
import os
import tarfile
import tempfile
import s3split.common


class Splitter():
    """split files in tar archives"""

    def __init__(self, event, s3manager, fs_path, split):
        self._logger = s3split.common.get_logger()
        if not event.is_set():
            self._logger.debug(f"Split: {split.get('id')} - Create Splitter class for split: {split}")
            self._s3manager = s3manager
            self._event = event
            # self._args = args
            self._fs_path = fs_path
            self._s3_bucket = s3manager.s3_bucket
            self._s3_path = s3manager.s3_path
            self.split = split
            # self.bucket = args.s3_bucket
            self.name_tar = f"s3split-part-{self.split.get('id')}.tar"
        else:
            self._logger.debug(f"Split: {split.get('id')} - Create Splitter class skipped because terminating event is set")

    def _tar(self):
        # Filter function to update tar path, required to untar in a safe location
        def tar_filter(tobj):
            new = tobj.name.replace(self._fs_path.strip('/'), self._s3_path.strip('/'))
            tobj.name = new
            return tobj
        if not self._event.is_set():
            self._logger.debug(f"Split: {self.split.get('id')} - Start create tar {self.name_tar}")
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_file = os.path.join(tmpdir, self.name_tar)
                with tarfile.open(tar_file, "w") as tar:
                    for path in self.split.get('paths'):
                        # remove base path from folder with filter function
                        tar.add(path, filter=tar_filter)
                    self._logger.debug(f"Split: {self.split.get('id')} - Generated tar file {tar_file}")
                    # Start upload
                    if not self._event.is_set():
                        self._s3manager.upload_file(tar_file)
                        return {"path": tar_file, "id": self.split.get('id'), "size": None}
                    self._logger.info(f"Split: {self.split.get('id')} - Upload interrupted because terminating event is set!")
                    return None
        else:
            self._logger.info(f"Split: {self.split.get('id')} - Tar interrupted because terminating event is set!")
            return None

    def run(self):
        """create a tar and upload"""
        self._logger.debug(f"Split: {self.split.get('id')} - Start processing")
        if not self._event.is_set():
            return self._tar()
        else:
            self._logger.info(f"Split: {self.split.get('id')} - processing interrupted because terminating event is set!")
            return None
