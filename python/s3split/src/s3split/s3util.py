
import boto3
import boto3.session
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
import urllib3

import src.s3split.common

logger = src.s3split.common.get_logger()
urllib3.disable_warnings()

class S3Manager():
    def check(self):
        print("---- example module ---")

    def __init__(self, args):
        self._args = args
        self._session = boto3.session.Session()
        self._client_config = botocore.config.Config(max_pool_connections=25)
        self._s3_client = None

    def get_client(self):
        if self._s3_client is None:
            # self._s3_client = self._session.client('s3', aws_access_key_id=self._args.s3_access_key, aws_secret_access_key=self._args.s3_secret_key,
            #                                        endpoint_url=self._args.s3_endpoint, use_ssl=self._args.s3_use_ssl, verify=False, config=self._client_config)
            try:
                self._s3_client = self._session.client('s3', aws_access_key_id=self._args.s3_access_key, aws_secret_access_key=self._args.s3_secret_key,
                                                       endpoint_url=self._args.s3_endpoint, use_ssl=self._args.s3_use_ssl, verify=False, config=self._client_config)
            except (ClientError, ValueError) as e:
                logger.error(f"S3 endpoint connection error - {e}")
                raise SystemExit("args validation error S3 endpoint")
        return self._s3_client
