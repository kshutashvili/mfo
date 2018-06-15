from django.db import models

from .storages import ProtectedFileSystemStorage


class ProtectedFileField(models.FileField):
    def __init__(self, **kwargs):
        kwargs["storage"] = ProtectedFileSystemStorage()
        super(ProtectedFileField, self).__init__(**kwargs)
