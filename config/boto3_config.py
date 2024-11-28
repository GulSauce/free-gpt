import os
from dotenv import load_dotenv
import boto3
from botocore.client import Config

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

class FileUploadInfo:
    def __init__(self, path: str, name:str, id:str, mime:str):
        self.path = path
        self.name = name
        self.id = id
        self.mime= mime

def upload_image_return_url(file_upload_info: FileUploadInfo):
    data = open(file_upload_info.path, 'rb')
    file_name = file_upload_info.name
    file_id = file_upload_info.id
    file_mime = file_upload_info.mime
    s3 = boto3.resource(
        's3',
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )

    full_file_name = f"{file_name}-{file_id}"
    s3.Bucket(S3_BUCKET_NAME).put_object(
        Key=full_file_name, Body=data, ContentType=file_mime)

    return f"https://gpt-files.sulmoon.io/{full_file_name}"