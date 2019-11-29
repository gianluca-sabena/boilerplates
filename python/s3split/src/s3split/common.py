import logging
import random
import os


def get_logger():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    # logger = logging.getLogger('s3cmd')
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # logger = logging.getLogger('s3cmd')
    # logger.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', "%H:%M:%S")
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)
    return logging

def split_file_by_size(path, max_size):
    def get_path_size(start_path):
        total_size = 0
        if os.path.isfile(start_path):
            return os.path.getsize(start_path)
        for dirpath, _, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    splits = []
    tar_size = 0
    tar_paths = []
    list = [os.path.join(path, f) for f in os.listdir(path)]
    random.shuffle(list)
    id = 1
    for p in list:
        size = get_path_size(p)
        # logger.debug(f"path: {p} - size: {size} - {tar_size + size} - {max_size * 1024 * 1024}")
        if size > (max_size * 1024 * 1024):
            raise SystemExit(f"Single path '{p}' has a size bigger then max allowed split size. Exit")
        if (tar_size + size) <= (max_size * 1024 * 1024):
            tar_size += size
            tar_paths.append(p)
        else:
            splits.append({'paths': tar_paths, 'size': tar_size, 'id': id})
            id += 1
            tar_size = size
            tar_paths = [p]
    if tar_size > 0:
        splits.append({'paths': tar_paths, 'size': tar_size, 'id': id})
    return splits