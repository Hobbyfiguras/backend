from haystack.fields import CharField
import random
from django.templatetags.static import static
from .avatars import get_avatar

class AvatarField(CharField):
    field_type = "avatar"
    def prepare(self, obj):
        random.seed(obj.id)
        value =  super(AvatarField, self).prepare(obj)
        return get_avatar(obj.id)