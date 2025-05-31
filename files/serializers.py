import mimetypes
from uuid import uuid4

import boto3
import boto3.exceptions
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from files.models import *


def get_object_metadata(object_key, bucket_name=settings.AWS_CLOUD_STORAGE_BUCKET_NAME):
    try:
        s3 = boto3.client(
            "s3",
            config=Config(signature_version="s3v4"),
        )
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
        metadata = {
            "content_length": response["ContentLength"],
            "content_type": response["ContentType"],
            "last_modified": response["LastModified"],
            "etag": response["ETag"],
            "meta_data": response.get("Metadata", {}),
        }
        return metadata
    except ClientError as e:
        logger.error(
            f"S3 ClientError: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None


class FileMetaSerializer(serializers.ModelSerializer):
    content_length = serializers.IntegerField(read_only=True)
    content_type = serializers.CharField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
    meta_data = serializers.JSONField(read_only=True)

    class Meta:
        model = FileMeta
        exclude = []
        read_only_fields = ["public_url"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        key = attrs.get("key")
        meta_data = get_object_metadata(key)

        if not meta_data:
            raise ValidationError({"key": ["invalid key"]})

        meta_data = {**meta_data, **attrs}

        return meta_data

    def create(self, validated_data):
        bucket_name = os.getenv("AWS_CLOUD_STORAGE_BUCKET_NAME")
        s3_region = os.getenv("AWS_CLOUD_S3_REGION_NAME", "eu-north-1")
        key = validated_data.get("key")
        return super().create(
            {
                "key": key,
                "public_url": f"https://{bucket_name}.s3.{s3_region}.amazonaws.com/{key}",
            }
        )


class SignedURLSerializer(serializers.Serializer):
    hash = serializers.CharField(max_length=255, write_only=True)
    extension_choices = [
        ("png", "png"),
        ("jpg", "jpg"),
        ("heic", "heic"),
        ("jpeg", "jpeg"),
        ("gif", "gif"),
        ("pdf", "pdf"),
        ("mp4", "mp4"),
        ("mkv", "mkv"),
        ("avi", "avi"),
    ]
    size = serializers.IntegerField(min_value=10, max_value=6000)
    ext = serializers.ChoiceField(choices=extension_choices, write_only=True)

    id = serializers.CharField(read_only=True)
    signed_url = serializers.CharField(read_only=True)
    key = serializers.CharField(read_only=True)

    def create(self, validated_data):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_CLOUD_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_CLOUD_SECRET_ACCESS_KEY,
            region_name=settings.AWS_CLOUD_S3_REGION_NAME,
            config=Config(signature_version="s3v4"),
        )
        file_id = uuid4()

        ext = validated_data.pop("ext")
        hash = validated_data.pop("hash")

        file_name = f"{hash}.{ext}"
        contentType = self.get_content_type(file_name)
        file_path = f"uploads/{file_name}"

        signed_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_CLOUD_STORAGE_BUCKET_NAME,
                "Key": file_path,
                "ContentType": contentType,
            },
            ExpiresIn=600,  # URL expires in 10 minutes
        )
        return {
            "signed_url": signed_url,
            "id": file_id,
            **validated_data,
            "key": file_path,
        }

    def get_content_type(self, file_path: str) -> str:
        """
        Determines the content type (MIME type) from a file extension.

        :param file_path: The file path or file name.
        :return: The MIME type as a string, or 'application/octet-stream' if unknown.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"
