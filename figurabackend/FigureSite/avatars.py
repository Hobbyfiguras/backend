import random
from django.templatetags.static import static

DEFAULT_AVATARS = [
        '/avatars/avatar_1.png',
        '/avatars/avatar_2.png',
        '/avatars/avatar_3.png'
    ]

def get_avatar(user):
    if user.avatar:
        return user.avatar.url
    else:
        random.seed(user.id)
        return static(random.choice(DEFAULT_AVATARS))