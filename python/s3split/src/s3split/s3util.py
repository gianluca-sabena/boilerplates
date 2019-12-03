
import boto3
import boto3.session
import botocore
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
import urllib3

import common

logger = common.get_logger()
urllib3.disable_warnings()


class S3Manager():
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
            except ValueError as ex:
                raise ValueError(f"S3 ValueError: {ex}")            
            except ClientError as ex:
                raise ValueError(f"S3 ClientError: {ex}")
        return self._s3_client

    def bucket_create(self, bucket):
        if not self.bucket_exsist(bucket):
            try:
                self._s3_client.create_bucket(Bucket=bucket)
            except ClientError as ex:
                if ex.response['Error']['Code'] == 'InvalidBucketName':
                    raise ValueError(f"S3 ClientError: {ex}")
                else:
                    return False
            else:
                return True

    def bucket_exsist(self, bucket):
        """Check if S3 bucket exsist

        :param bucket_name: Bucket to create
        :return: True if bucket is present, else False
        """

        # Check if a bucket exsists https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html?highlight=clienterror#accessing-a-bucket
        try:
            self._s3_client.head_bucket(Bucket=bucket)
        except ValueError as e:
            raise ValueError(f"S3 ValueError: {e}")            
        except ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(e, e.response)
                raise ValueError(f"S3 ClientError: {e}")
        else:
            return True
