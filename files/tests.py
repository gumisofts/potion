from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FileModel


class FileUploadDownloadTests(APITestCase):

    def setUp(self):
        """Set up the test with an image file."""
        # self.upload_url = reverse("file-upload-list")  # Update this if needed
        # self.download_url_template = reverse('file-download', kwargs={'stored_as': 'test_stored_as'})  # Placeholder

        def generate_test_image():
            """Generate a simple in-memory image for testing"""
            image = Image.new("RGB", (100, 100), color=(255, 0, 0))
            image_io = BytesIO()
            image.save(image_io, format="JPEG")
            image_io.seek(0)
            return image_io

        self.sample_file = SimpleUploadedFile(
            "test_image.jpg", generate_test_image().read(), content_type="image/jpeg"
        )

    # def test_upload_file(self):
    #     """Test that a file can be uploaded successfully."""
    #     data = {"file": self.sample_file, "alt_text": "Test Image Alt Text"}

    #     response = self.client.post(self.upload_url, data, format="multipart")

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn("stored_as", response.data)  # Ensure stored_as is in response

    #     # Check that the file was actually stored in the database
    #     stored_as = response.data["stored_as"]
    #     self.assertTrue(FileModel.objects.filter(stored_as=stored_as).exists())
