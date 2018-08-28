import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField

class AvatarRename(object):
    def __call__(self, instance, filename):
        # Remove the extension from the filename
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(instance.id, ext)
        # return the whole path to the file
        return os.path.join("avatars", filename)


class User(AbstractUser):
    avatar = ResizedImageField(size=[256, 256], crop=['middle', 'center'], force_format='JPEG',upload_to=AvatarRename(), null=True, blank=True)
