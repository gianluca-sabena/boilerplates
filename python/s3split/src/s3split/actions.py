"""main actions: upload, check"""
import os
import traceback
import concurrent.futures
import s3split.s3util
import s3split.common
import s3split.splitter


def action_check(event, args):
    """download splits to s3"""
    logger = s3split.common.get_logger()
    stats = s3split.s3util.Stats()
    # Validate
    if not os.path.isdir(args.source):
        raise ValueError(f"source: '{args.source}' is not a directory")
    s3uri = s3split.s3util.S3Uri(args.target)
    s3_manager = s3split.s3util.S3Manager(args.s3_access_key, args.s3_secret_key, args.s3_endpoint,
                                          args.s3_use_ssl, s3uri.bucket, s3uri.object, stats)
    s3_manager.bucket_create(s3uri.bucket)
    objects = s3_manager.list_bucket_objects()
    metadata = s3_manager.download_metadata()
    tar_data = {tar['name']: tar['size'] for tar in metadata["tars"]}
    s3_data = {obj['Key']: obj['Size'] for obj in objects}
    #LOGGER.info(pformat(objects))
    #LOGGER.info(pformat(metadata))
    #LOGGER.info(pformat(tar_data))
    #LOGGER.info(pformat(s3_data))
    errors = False
    if len(metadata["splits"]) != len(metadata["tars"]):
        logger.error("Number of slplits and tar files is different! Incomplete upload!")
        errors = True
    for key, val in tar_data.items():
        if s3_data.get(key) is None:
            logger.error(f"Split part {key} not found on S3! Inclomplete uploads detected!")
            errors = True
        elif s3_data.get(key) == val:
            logger.info(f"Check size for split part {key}: OK")
        elif s3_data.get(key) != val:
            logger.error(f"Check size for split part {key} failed! Expected size: {val} comparade to s3 object size: {s3_data.get('key')} ")
            errors = True
    return not errors

def action_upload(event, args):
    """upload splits to s3"""
    logger = s3split.common.get_logger()
    stats = s3split.s3util.Stats(args.stats_interval)
    logger = s3split.common.get_logger()
    logger.info(f"Tar object max size: {args.tar_size} MB")
    # Validate
    if not os.path.isdir(args.source):
        raise ValueError(f"source: '{args.source}' is not a directory")
    s3_uri = s3split.s3util.S3Uri(args.target)
    s3_manager = s3split.s3util.S3Manager(args.s3_access_key, args.s3_secret_key, args.s3_endpoint,
                                          args.s3_use_ssl, s3_uri.bucket, s3_uri.object, stats)
    s3_manager.bucket_create(s3_uri.bucket)
    logger.info(f"Upload started! Print stats evry: {args.stats_interval} seconds")
    # Upload metadata file
    splits = s3split.common.split_file_by_size(args.source, args.tar_size)
    tars_uploaded = []
    future_split = {}
    if not s3_manager.upload_metadata(splits):
        logger.error("Metadata json file upload failed!")
        raise SystemExit
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        for split in splits:
            s3manager = s3split.s3util.S3Manager(args.s3_access_key, args.s3_secret_key, args.s3_endpoint,
                                                 args.s3_use_ssl, s3_uri.bucket, s3_uri.object, stats)
            splitter = s3split.splitter.Splitter(event, s3manager, args.source, split)
            future = executor.submit(splitter.run)
            future_split.update({future: split.get('id')})
        logger.debug(f"List of futures: {future_split}")
        for future in concurrent.futures.as_completed(future_split):
            try:
                data = future.result()
                tars_uploaded.append(data)
            except Exception as exc: # pylint: disable=broad-except
                logger.error(f"generated an exception: {exc}")
                traceback_str = traceback.format_exc(exc)
                logger.error(f"generated an exception: {traceback_str}")
            else:
                logger.info(f"Split: {data['id']} Completed task processing")
    logger.debug(f"Tars uploaded completed - tars: {tars_uploaded}")
    if not s3_manager.upload_metadata(splits, tars_uploaded):
        logger.error("Metadata json file upload failed!")
        raise SystemExit
    stats.print()
    # upload metadata with tars info
