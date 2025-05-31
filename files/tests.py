from io import BytesIO
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from files.models import FileMeta

User = get_user_model()


class SignUrlViewsetTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("signed-url-list")

    def test_successful_signed_url_request(self):
        payload = {"hash": "examplehash", "size": 500, "ext": "jpg"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("signed_url", response.data)

    def test_invalid_extension_request(self):
        payload = {"hash": "examplehash", "size": 500, "ext": "exe"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ext", response.data)

    def test_missing_fields_request(self):
        payload = {
            "hash": "examplehash",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("size", response.data)
        self.assertIn("ext", response.data)

    def test_unauthenticated_request(self):
        self.client.logout()
        payload = {"hash": "examplehash", "size": 500, "ext": "jpg"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FileMetaDataViewsetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="testuser", phone_number="912345678", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("file-meta-list")

        # Create a test file metadata entry
        self.file_meta = FileMeta.objects.create(
            key="test/file.jpg",
            public_url="https://test-bucket.s3.eu-north-1.amazonaws.com/test/file.jpg",
        )

    def test_create_file_metadata_success(self):
        """Test creating a new file metadata entry"""
        payload = {"key": "uploads/string.jpeg"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("key", response.data)
        self.assertIn("public_url", response.data)

    def test_create_file_metadata_invalid_key(self):
        """Test creating file metadata with invalid key"""
        payload = {"key": "nonexistent/file.jpg"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("key", response.data)

    def test_list_file_metadata(self):
        """Test listing all file metadata entries"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the one we created in setUp
        self.assertEqual(response.data[0]["key"], self.file_meta.key)
        self.assertEqual(response.data[0]["public_url"], self.file_meta.public_url)

    def test_retrieve_file_metadata(self):
        """Test retrieving a single file metadata entry"""
        url = reverse("file-meta-detail", args=[self.file_meta.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["key"], self.file_meta.key)
        self.assertEqual(response.data["public_url"], self.file_meta.public_url)

    def test_retrieve_nonexistent_file_metadata(self):
        """Test retrieving a nonexistent file metadata entry"""
        url = reverse("file-meta-detail", args=[uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test accessing endpoints without authentication"""
        self.client.logout()

        # Test list endpoint
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test create endpoint
        payload = {"key": "uploads/test.jpg"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test retrieve endpoint
        url = reverse("file-meta-detail", args=[self.file_meta.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
