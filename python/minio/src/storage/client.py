from minio import Minio
from minio.error import ResponseError
import urllib3


class Client:
    minio_client = None

    def __init__(self, host, access_key, secret_key):
        urllib3.disable_warnings()
        self.http_client = urllib3.PoolManager(timeout=urllib3.Timeout.DEFAULT_TIMEOUT, cert_reqs='CERT_NONE')
        print(f"host: {host}")
        print(f"accessKey: {access_key}")
        print(f"secretKey: {secret_key}")
        self.minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=True, http_client=self.http_client)

    def get_client(self):
        return self.minio_client

    def list_objects(self, bucket):
        objects = self.minio_client.list_objects_v2(bucket, prefix="", recursive=True)
        file_list = [obj.object_name for obj in objects]
        print(files)
