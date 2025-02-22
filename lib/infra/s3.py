import json
import tempfile
import boto3
import os
import logging
from io import BytesIO

from src.app import App

logging.basicConfig(level=logging.INFO)


class File:
    def __init__(self, filename: str):
        self.filename = filename


class S3:
    AWS_REGION = ''
    AWS_BUCKET_NAME = ''

    def __init__(self):
        self.resource = boto3.resource('s3', region_name=self.AWS_REGION)
        self.client = self.resource.meta.client
        self.bucket = self.AWS_BUCKET_NAME

    @classmethod
    def init_app(cls, app: App):
        cls.AWS_REGION = app.config['AWS_REGION']
        cls.AWS_BUCKET_NAME = app.config['AWS_BUCKET_NAME']

    def deserialize_json(json_obj) -> BytesIO:
        file_content = json.dumps(json_obj).encode("utf-8")
        deserialized = BytesIO(file_content)
        return deserialized

    def serialize_json_files(self, file_keys, bucket=None) -> list:
        if bucket is None:
            bucket = self.bucket
        try:
            res = []
            for file_key in file_keys:
                file_obj = BytesIO()
                self.client.download_fileobj(bucket, file_key, file_obj)
                file_obj.seek(0)
                json_data = json.load(file_obj)
                res.append(json_data)
            return res
        except Exception as e:
            return None

    def get_files_from_dir(self, dir_name, bucket=None):
        if bucket is None:
            bucket = self.bucket
        try:
            response = self.client.list_objects_v2(
                Bucket=bucket, Prefix=dir_name)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logging.error(
                f"❌ Error occured while reading file list in {bucket} bucket: {e}")
            return []

    def get_file(self, path: str, bucket=None) -> str:
        if bucket is None:
            bucket = self.bucket

        local_path = os.path.join(
            tempfile.gettempdir(), os.path.basename(path))
        try:
            self.client.download_file(bucket, path, local_path)
            logging.info(
                f"✅ Successfully downloaded the file from S3: {path} → {local_path}")
            return local_path
        except Exception as e:
            logging.error(
                f"❌ Failed downloading the file from S3 ({bucket}/{path}): {e}")
            return None

    def upload_file(self, file_local_path, file_s3_path, bucket=None):
        if bucket is None:
            bucket = self.bucket
        try:
            if file_s3_path is None:
                file_s3_path = os.path.basename(file_local_path)

            self.client.upload_file(file_local_path, bucket, file_s3_path)

            object_url = f"https://{bucket}.s3.amazonaws.com/{file_s3_path}"
            logging.info(
                f"✅ Successfully uploaded the file to S3: {object_url}")
            return object_url
        except Exception as e:
            logging.error(
                f"❌ Failed uploading the file to S3 ({file_local_path} → {bucket}/{file_s3_path}): {e}")
            return None

    def upload_file_object(self, file_obj: BytesIO, file_s3_path, bucket=None):
        if bucket is None:
            bucket = self.bucket
        try:
            if file_s3_path is None:
                file_s3_path = file_obj.filename

            file_obj.seek(0)
            self.client.upload_fileobj(file_obj, bucket, file_s3_path)

            object_url = f"https://{bucket}.s3.amazonaws.com/{file_s3_path}"
            logging.info(
                f"✅ Successfully uploaded a file object to S3: {object_url}")
            return object_url
        except Exception as e:
            logging.error(
                f"❌ Failed uploading a file object to S3 ({file_obj.filename} → {bucket}/{file_s3_path}): {e}")
            return None

    def delete_file_object(self, file_s3_path, bucket=None):
        if bucket is None:
            bucket = self.bucket
        try:
            self.client.delete_object(Bucket=bucket, Key=file_s3_path)
            logging.info(f"✅ Removed file from S3: {file_s3_path}")
        except Exception as e:
            logging.error(
                f"❌ Failed removing file from S3 ({file_s3_path}): {e}")

    def copy_s3_file(self, source_bucket, source_key, destination_bucket, destination_key):
        try:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            self.client.copy(copy_source, destination_bucket, destination_key)

            s3_url = f"https://{destination_bucket}.s3.amazonaws.com/{destination_key}"
            logging.info(
                f"✅ File copied successfully: {source_bucket}/{source_key} → {destination_bucket}/{destination_key}")
            return s3_url
        except Exception as e:
            logging.error(
                f"❌ Failed copying file ({source_bucket}/{source_key} → {destination_bucket}/{destination_key}): {e}")
            return None
