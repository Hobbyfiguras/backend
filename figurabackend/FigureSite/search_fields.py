from haystack.fields import CharField, SearchField, DecimalField
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

class ClassifiedImageField(CharField):
    field_type = "string"
    def prepare(self, obj):
        images = obj.images.all()
        image = images[0]
        for img in images:
            if img.primary:
                image = img
        return image.image.url
class MoneyField(DecimalField):
    field_type = "float"
    def prepare(self, obj):
        return obj.price.amount