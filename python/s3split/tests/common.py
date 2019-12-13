"shared test functions"
import os
import s3split.common

LOGGER = s3split.common.get_logger()

def generate_random_files(full_path, n_files, size):
    """path, n_files, number of files file size in kb"""
    if not os.path.isdir(full_path):
        try:
            os.makedirs(full_path)
        except OSError as ex:
            LOGGER.error(f"Creation of the directory {full_path} failed - {ex}")
        else:
            LOGGER.info(f"Successfully created the directory {full_path}")
    for i in range(n_files):
        with open(os.path.join(full_path, f"file_{i+1}.txt"), 'wb') as fout:
            fout.write(os.urandom(size * 1024))