from haystack.fields import CharField, SearchField
import random
from django.templatetags.static import static
from .avatars import get_avatar

class AvatarField(CharField):
    field_type = "string"
    def prepare(self, obj):
        random.seed(obj.id)
        value = super(AvatarField, self).prepare(obj)
        print(value)
        return get_avatar(obj.creator)

class UserAvatarField(CharField):
    field_type = "string"
    def prepare(self, obj):
        random.seed(obj.id)
        return get_avatar(obj)