import mimetypes
import urllib.parse
from uuid import uuid4

import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import FileField, ModelSerializer

from .models import FileModel


class FileDownloadSerializer(serializers.Serializer):
    message = serializers.CharField(default="File retrieved successfully")
    file_url = serializers.SerializerMethodField()
    optimized_image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    alt_text = serializers.CharField(required=False)
    error = serializers.CharField(required=False)

    def get_file_url(self, obj):
        """Returns the original file URL"""
        if hasattr(obj, "file") and obj.file:
            return obj.file.url  # Original file
        return None

    def get_optimized_image_url(self, obj):
        """Returns the optimized image URL if available"""
        if hasattr(obj, "optimized_image") and obj.optimized_image:
            return obj.optimized_image.url  # Optimized version
        return None

    def get_thumbnail_url(self, obj):
        """Returns the thumbnail URL if available"""
        if hasattr(obj, "thumbnail") and obj.thumbnail:
            return obj.thumbnail.url  # Thumbnail version
        return None


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

    def validate(self, attrs):

        attrs = super().validate(attrs)
        if attrs.get("ext") not in [s[0] for s in self.extension_choices]:
            raise ValidationError({"ext": "unsupported extension"})

        return attrs

    def create(self, validated_data):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
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
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": file_path,
                "ContentType": contentType,
            },
            ExpiresIn=600,  # URL expires in 10 minutes
        )
        return {"signed_url": signed_url, "id": file_id, **validated_data}

    def get_content_type(self, file_path: str) -> str:
        """
        Determines the content type (MIME type) from a file extension.

        :param file_path: The file path or file name.
        :return: The MIME type as a string, or 'application/octet-stream' if unknown.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"


class FileUploadSerializer(ModelSerializer):
    file = FileField()

    class Meta:
        model = FileModel
        fields = ["file", "alt_text"]
        read_only_fields = ["stored_as"]


class FileMetadataSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    file_size = serializers.IntegerField()
    alt_text = serializers.CharField(required=False, allow_blank=True)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = []
        model = FileModel


class SignedUrlSerializer(serializers.Serializer):
    signed_url = serializers.CharField()
    file_name = serializers.CharField()
