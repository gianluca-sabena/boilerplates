import logging



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
