from django.db import models

from .storages import ProtectedFileSystemStorage


class ProtectedFileField(models.FileField):
    def __init__(self, **kwargs):
        if "storage" in kwargs:
            raise Exception()
        super(ProtectedFileField, self).__init__(
            storage=ProtectedFileSystemStorage, **kwargs
        )
