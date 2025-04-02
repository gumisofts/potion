import os
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet

from files.serializers import *
from files.spectacular_schema import (
    file_download_schema,
    file_upload_schema,
)

from .models import FileModel
from .serializers import FileDownloadSerializer, FileUploadSerializer


class SignUrlViewset(CreateModelMixin, GenericViewSet):
    serializer_class = SignedURLSerializer
    permission_classes = [IsAuthenticated]


class GenerateSignedUrlView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SignedUrlSerializer

    def get(self, request):
        """Generate a signed URL for direct S3 upload."""
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version="s3v4"),
        )
        file_id = uuid4()

        file_name = f"{file_id}.{request.query_params.get('ext')}"
        file_path = f"uploads/{file_name}"

        try:
            signed_url = s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": file_path,
                    "ContentType": request.query_params.get(
                        "content_type", "application/octet-stream"
                    ),
                },
                ExpiresIn=600,  # URL expires in 10 minutes
            )

            return Response(
                {"signed_url": signed_url, "file_name": file_name, "id": file_id}
            )

        except NoCredentialsError:
            return Response({"error": "AWS credentials not found"}, status=500)


class SaveUploadedFileView(APIView):

    def post(self, request):
        """Update file metadata after direct S3 upload"""
        stored_as = request.data.get("stored_as")
        file_size = request.data.get("file_size", 0)
        alt_text = request.data.get("alt_text", "")

        try:
            file_instance = FileModel.objects.get(stored_as=stored_as)

            file_instance.file_size = file_size
            file_instance.alt_text = alt_text
            file_instance.file_extension = os.path.splitext(file_instance.name)[
                1
            ].lower()

            file_instance.save()

            return Response(
                {
                    "message": "File metadata updated successfully",
                    "stored_as": file_instance.stored_as,
                }
            )

        except FileModel.DoesNotExist:
            return Response({"message": "File not found"}, status=404)


class UploadViewSet(ViewSet):
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    @file_upload_schema
    def create(self, request):
        my_file = FileUploadSerializer(data=request.data)
        if my_file.is_valid():
            saved_file = my_file.save()
            response = {
                "message": "File uploaded successfully",
                "stored_as": saved_file.stored_as,
            }
        else:
            response = {"message": "Invalid request", "errors": my_file.errors}

        return Response(response)


class FileViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]


class FileDownloadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @file_download_schema
    def get(self, request, stored_as):

        file_instance = get_object_or_404(FileModel, stored_as=stored_as)

        response_data = FileDownloadSerializer(file_instance).data
        return Response(response_data)
