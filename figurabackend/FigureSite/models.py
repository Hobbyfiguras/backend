import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
from django.db import models
from django.utils.deconstruct import deconstructible
from ordered_model.models import OrderedModel
@deconstructible

class AvatarRename(object):
    def __call__(self, instance, filename):
        # Remove the extension from the filename
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(instance.id, ext)
        # return the whole path to the file
        return os.path.join("avatars", filename)

avatar_rename = AvatarRename()

class User(AbstractUser):
    avatar = ResizedImageField(size=[256, 256], crop=['middle', 'center'], force_format='JPEG', upload_to=avatar_rename, null=True, blank=True)

class ForumCategory(OrderedModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "forum categories"

class Forum(OrderedModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(ForumCategory, related_name="forums", on_delete=models.CASCADE)
    def __str__(self):
        return self.name