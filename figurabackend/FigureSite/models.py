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
from django.db import IntegrityError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from rest_framework_serializer_extensions.utils import external_id_from_model_and_internal_id
from django.apps import apps
from django.utils import timezone
from mfc import mfc_api
from django.http import Http404
from guardian.mixins import GuardianUserMixin


class MyUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)


@deconstructible
class AvatarRename(object):
    def __call__(self, instance, filename):
        # Remove the extension from the filename
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(external_id_from_model_and_internal_id(
            apps.get_model(app_label="FigureSite", model_name="User"), instance.id), ext)
        print("avatar: %s" % filename)
        # return the whole path to the file
        return os.path.join("avatars", filename)


@deconstructible
class ForumIconRename(object):
    def __call__(self, instance, filename):
        # Remove the extension from the filename
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(instance.slug, ext)
        # return the whole path to the file
        return os.path.join("forum_icons", filename)


@deconstructible
class VoteTypeRename(object):
    def __call__(self, instance, filename):
        # Remove the extension from the filename
        ext = filename.split('.')[-1]

        filename = '{}.{}'.format(instance.slug, ext)
        # return the whole path to the file
        return os.path.join("forum_votes", filename)


avatar_rename = AvatarRename()
forum_icon_rename = ForumIconRename()
vote_type_rename = VoteTypeRename()


class User(AbstractUser, GuardianUserMixin):
    objects = MyUserManager()
    avatar = ResizedImageField(size=[256, 256], crop=[
                               'middle', 'center'], force_format='JPEG', upload_to=avatar_rename, null=True, blank=True)
    mal_username = models.CharField(max_length=80, null=True, blank=True)
    anilist_username = models.CharField(max_length=80, null=True, blank=True)
    mfc_username = models.CharField(max_length=80, null=True, blank=True)
    twitter_username = models.CharField(max_length=80, null=True, blank=True)
    nsfw_enabled = models.BooleanField(default=False)
    location = models.TextField(max_length=100, default='')
    bio = models.TextField(max_length=10000, default='', null=True, blank=True)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD + '__iexact': username})

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_ban_user_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_ban_user_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_send_message_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_send_message_permission(self, request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_update_permission(request):
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        print(self.id)
        print(request.user.id)
        if self == request.user:
            return True
        else:
            return False

    @property
    def is_banned(self):
        if self.bans.count() > 0:
            if self.bans.all()[self.bans.count() - 1].ban_expiry_date > timezone.now():
                return True
        return False

    def has_object_update_permission(self, request):
        print(self.id)
        print(request.user.id)
        if self == request.user:
            return True


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
        super(ForumCategory, self).save(*args, **kwargs)


class Forum(OrderedModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    category = models.ForeignKey(
        ForumCategory, related_name="forums", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, blank=True, unique=True)
    only_staff_can_post = models.BooleanField(default=False)
    icon = ResizedImageField(size=[128, 128], crop=[
                             'middle', 'center'], upload_to=forum_icon_rename, force_format='PNG', null=True, blank=True)
    order_with_respect_to = 'category'

    class Meta:
        permissions = (
            ('change_threads_subscription', 'Change subscription status in forum'),
            ('move_threads', 'Move threads in forum'),
            ('make_threads_nsfw', 'Make thread be NSFW in forum'),
            ('create_threads', 'Create threads in forum')
        )

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_create_thread_permission(request):
        if not request.user.is_banned:
            return True
        else:
            return False

    @authenticated_users
    def has_object_create_thread_permission(self, request):
        if self.only_staff_can_post:
            return request.user.is_staff
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(request):
        return False

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Only save slugs on first save
        if not self.id:
            unique_slugify(self, self.name)
        super(Forum, self).save(*args, **kwargs)


class PrivateMessage(models.Model):
    creator = models.ForeignKey(
        User, related_name="messages_sent", on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, related_name="messages_received", on_delete=models.CASCADE)
    subject = models.TextField(max_length=500)
    content = models.TextField(max_length=20000)
    created = models.DateTimeField(editable=False)
    read = models.BooleanField(default=False)

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        if self.creator == request.user or self.receiver == request.user:
            return True
        else:
            return False

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        if self.creator == request.user or self.receiver == request.user:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(PrivateMessage, self).save(*args, **kwargs)


class MFCItem(models.Model):
    name = models.TextField()
    created = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(MFCItem, self).save(*args, **kwargs)

    @classmethod
    def get_or_fetch_mfc_item(cls, id):
        try:
            item = cls.objects.get(id=id)
        except cls.DoesNotExist as err:
            try:
                mfc_item = mfc_api.get_figure_data(id)
            except:
                return None
            # HACK: Django doesn't really call our overriden save method from inside a classmethod, so we have to add created here
            item = cls(id=mfc_item['id'],
                       name=mfc_item['name'], created=timezone.now())
            item.save()
        return item


class Thread(models.Model):
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(
        User, related_name="threads", on_delete=models.CASCADE)
    forum = models.ForeignKey(
        Forum, related_name="threads", on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    slug = models.SlugField(max_length=100, blank=True, unique=True)
    nsfw = models.BooleanField(default=False)
    is_sticky = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(
        User, related_name="subscribed_threads")
    related_items = models.ManyToManyField(
        MFCItem, related_name="related_threads")
    highlighted = models.BooleanField(default=False)

    @property
    def hid(self):
        return external_id_from_model_and_internal_id(Thread, self.id)

    @property
    def post_count(self):
        return self.posts.count()

    def change_user_subscription(self, user, subscribed):
        if subscribed:
            self.subscribers.add(user)
        else:
            self.subscribers.remove(user)
        self.save()

    @staticmethod
    @authenticated_users
    def has_update_permission(request):
        if not request.user.is_banned:
            return True
        else:
            return False

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        if self.creator == request.user:
            return True
        else:
            return False

    @staticmethod
    @authenticated_users
    def has_make_nsfw_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_make_nsfw_permission(self, request):
        if self.creator == request.user:
            return True
        else:
            return False

    @staticmethod
    @authenticated_users
    def has_move_thread_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_move_thread_permission(self, request):
        return False

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            self.modified = timezone.now()
        unique_slugify(self, self.title)
        return super(Thread, self).save(*args, **kwargs)

    @property
    def last_post(self):
        ordered_posts = self.posts.all().order_by('-created')
        if ordered_posts.count() > 0:
            return self.posts.all().order_by('-created')[0]
        else:
            return None

    @property
    def first_post(self):
        ordered_posts = self.posts.all().order_by('created')
        if ordered_posts.count() > 0:
            return ordered_posts[0]
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
        if not request.user.is_banned:
            return True
        else:
            return False

    @authenticated_users
    def has_object_create_post_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_change_subscription_permission(request):
        return True

    @authenticated_users
    def has_object_change_subscription_permission(self, request):
        return True

    def __str__(self):
        return self.title


class Post(models.Model):
    creator = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE)
    thread = models.ForeignKey(
        Thread, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField(max_length=40000)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField(editable=False)
    deleted = models.BooleanField(default=False)
    delete_reason = models.TextField(default='')
    modified_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)

    @property
    def hid(self):
        return external_id_from_model_and_internal_id(Post, self.id)

    @property
    def page(self):
        return int(self.__class__.objects.filter(thread=self.thread).filter(
            created__gt=self.created).count() / 20 + 1)

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @authenticated_users
    def has_write_permission(request):
        return True

    @authenticated_users
    def has_object_write_permission(self, request):
        if (request.user.id == self.creator.id and not request.user.is_banned) or request.user.is_staff:
            return True
        else:
            return False

    @staticmethod
    @authenticated_users
    def has_object_report_permission():
        return True

    @authenticated_users
    def has_object_report_permission(self, request):
        if request.user.id != self.creator.id:
            return True

    @staticmethod
    @authenticated_users
    def has_vote_permission(request):
        if not request.user.is_banned:
            return True
        else:
            return False

    @authenticated_users
    def has_object_vote_permission(self, request):
        return True

    def vote(self, user, vote_type):
        if user == self.creator:
            return 'self_vote'
        try:
            self.votes.create(user=user, post=self, vote_type=vote_type)
        except IntegrityError:
            return 'already_upvoted'
        return 'ok'

    def report(self, user, reason=''):
        try:
            self.reports.create(creator=user, post=self, reason=reason)
        except IntegrityError:
            return 'already_reported'
        return 'ok'

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
            self.modified = timezone.now()
        return super(Post, self).save(*args, **kwargs)


class Report(models.Model):
    creator = models.ForeignKey(
        User, related_name="reports", on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, related_name="reports", on_delete=models.CASCADE)
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
            self.created = timezone.now()
        return super(Report, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('creator', 'post')


class VoteType(OrderedModel):
    name = models.CharField(max_length=80)
    icon = ResizedImageField(size=[32, 32], crop=[
                             'middle', 'center'], force_format='PNG', upload_to=vote_type_rename)
    slug = models.SlugField(max_length=100, blank=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Only save slugs on first save
        if not self.id:
            unique_slugify(self, self.name)
        super(VoteType, self).save(*args, **kwargs)


class UserVote(models.Model):
    user = models.ForeignKey(User, related_name="votes",
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="votes",
                             on_delete=models.CASCADE)
    vote_type = models.ForeignKey(
        VoteType, related_name="votes", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')


class Notification(models.Model):
    # notification_post_sub
    notification_type = models.CharField(max_length=200)
    created = models.DateTimeField(editable=False)
    actor = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='notifications', on_delete=models.CASCADE)
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    notification_object = GenericForeignKey('object_type', 'object_id')
    read = models.BooleanField(default=False)

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        return request.user == self.user

    @staticmethod
    @authenticated_users
    def has_update_permission(request):
        return True

    @authenticated_users
    def has_object_update_permission(self, request):
        return request.user == self.user

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(Notification, self).save(*args, **kwargs)


class BanReason(models.Model):
    # notification_post_sub
    created = models.DateTimeField(editable=False)
    post = models.ForeignKey(Post, related_name="bans",
                             on_delete=models.CASCADE, null=True, blank=True)
    ban_reason = models.TextField(max_length=1000)
    banned_user = models.ForeignKey(
        User, related_name="bans", on_delete=models.CASCADE)
    banner = models.ForeignKey(
        User, related_name="+", on_delete=models.CASCADE)
    ban_expiry_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        return super(BanReason, self).save(*args, **kwargs)
