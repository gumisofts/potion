import io
import logging
import os
from uuid import uuid4

from django.db import models

logger = logging.getLogger(__name__)


class FileMeta(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    public_url = models.CharField(max_length=255)
