import io
import logging
import os
from uuid import uuid4

from django.db import models

from core.models import BaseModel

logger = logging.getLogger(__name__)


class FileMeta(BaseModel):
    key = models.CharField(max_length=255)
    public_url = models.CharField(max_length=255)
