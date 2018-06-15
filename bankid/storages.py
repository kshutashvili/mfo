from django.conf import settings
from django.core.files.storage import FileSystemStorage


class ProtectedFileSystemStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs["location"] = settings.PROTECTED_MEDIA_ROOT
        kwargs["base_url"] = settings.PROTECTED_MEDIA_URL
        super(ProtectedFileSystemStorage, self).__init__(*args, **kwargs)
