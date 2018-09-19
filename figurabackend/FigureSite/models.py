import os
import random
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django_resized import ResizedImageField
from django.db import models
from django.utils.deconstruct import deconstructible
from ordered_model.models import OrderedModel
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users
from .utils import unique_slugify
import datetime

class MyUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)

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
    objects = MyUserManager()
    avatar = ResizedImageField(size=[256, 256], crop=['middle', 'center'], force_format='JPEG', upload_to=avatar_rename, null=True, blank=True)
    mal_username = models.CharField(max_length=80, null=True, blank=True)
    anilist_username = models.CharField(max_length=80, null=True, blank=True)
    mfc_username = models.CharField(max_length=80, null=True, blank=True)
    twitter_username = models.CharField(max_length=80, null=True, blank=True)
    nsfw_enabled = models.BooleanField(default=False)
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD + '__iexact': username})
class ForumCategory(OrderedModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=100, blank=True, unique=True)


    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return False

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "forum categories"
    def save(self, *args, **kwargs):
        # Only save slugs on first save
        if not self.id:
            unique_slugify(self, self.name)
        super(ForumCategory, self).save(*args,**kwargs)

class Forum(OrderedModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(ForumCategory, related_name="forums", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, blank=True, unique=True)
    only_staff_can_post = models.BooleanField(default=False)

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_create_thread_permission(self):
        return True

    @authenticated_users
    def has_object_create_thread_permission(self, request):
        if self.only_staff_can_post:
            return request.user.is_staff
        return True

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        # Only save slugs on first save
        if not self.id:
            unique_slugify(self, self.name)
        super(Forum, self).save(*args,**kwargs)    

class Thread(models.Model):
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(User, related_name="threads", on_delete=models.CASCADE)
    forum = models.ForeignKey(Forum, related_name="threads", on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    slug = models.SlugField(max_length=100, blank=True, unique=True)
    nsfw = models.BooleanField(default=False)
    is_sticky = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.now()
            self.modified = datetime.datetime.now()
        unique_slugify(self, self.title)
        return super(Thread, self).save(*args, **kwargs)
    @property
    def last_post(self):
        ordered_posts = self.posts.all().order_by('-modified')
        if ordered_posts.count() > 0:
            return self.posts.all().order_by('-modified')[0]
        else:
            return None

    @property
    def first_post(self):
        ordered_posts = self.posts.all().order_by('modified')
        if ordered_posts.count() > 0:
            return self.posts.all().order_by('modified')[0]
        else:
            return None

    @staticmethod
    def has_read_permission(request):
        return True
    
    def has_object_read_permission(self, request):
        return True
    
    @staticmethod    
    @authenticated_users
    def has_create_post_permission(request):
        return True
    @authenticated_users
    def has_object_create_post_permission(self, request):
        return True

    def __str__(self):
        return self.title

class Post(models.Model):
    creator = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField(max_length=20000)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    deleted = models.BooleanField(default=False)
    delete_reason = models.TextField(default='')
    modified_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    
    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_object_write_permission(self, request):
        if request.user.id == self.creator.id or request.user.is_staff:
            return True
        else:
            return False
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = datetime.datetime.now()
            self.modified = datetime.datetime.now()
        return super(Post, self).save(*args, **kwargs)

    
class Report(models.Model):
    creator = models.ForeignKey(User, related_name="reports", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="reports", on_delete=models.CASCADE)
    reason = models.TextField()
    created = models.DateTimeField(editable=False)

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_read_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return False

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = datetime.datetime.now()
        return super(Report, self).save(*args, **kwargs)