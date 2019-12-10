"""main actions: upload, check"""
import os
import traceback
import concurrent.futures
import s3split.s3util
import s3split.common
import s3split.splitter


def action_upload(event, args):
    """upload splits to s3"""
    logger = s3split.common.get_logger()
    logger.info(f"Action: {args.action} {args.source} {args.target}")
    logger.info(f"Tar object max size: {args.tar_size} MB")
    stats = s3split.s3util.Stats(args.stats_interval)
    # TODO: validate args
    if not os.path.isdir(args.source):
        raise ValueError(f"source: '{args.source}' is not a directory")
    s3uri = s3split.s3util.S3Uri(args.target)
    # Test s3 connection
    s3_manager = s3split.s3util.S3Manager(args.s3_access_key, args.s3_secret_key, args.s3_endpoint,
                                          args.s3_use_ssl, s3uri.bucket, s3uri.object, stats)
    # Test write access to bucket
    s3_manager.bucket_create(s3uri.bucket)
    # Upload metadata file
    splits = s3split.common.split_file_by_size(args.source, args.tar_size)
    if not s3_manager.upload_metadata(splits):
        logger.error("Metadata json file upload failed!")
        raise SystemExit
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:

        # Start the load operations and mark each future with its URL
        # future_split = {executor.submit(splitter.Splitter, event, args, stats, split): split for split in splits}
        future_split = {}
        tars_uploaded = []
        for split in splits:
            s3manager = s3split.s3util.S3Manager(args.s3_access_key, args.s3_secret_key, args.s3_endpoint,
                                                 args.s3_use_ssl, s3uri.bucket, s3uri.object, stats)
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
    logger.info(f"tars: {tars_uploaded}")
    stats.print()
    # upload metadata with tars info
