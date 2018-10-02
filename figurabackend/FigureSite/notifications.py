
from . import serializers

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification(request, notification):
    actor_serializer = serializers.PublicUserSerializer(notification.notification_users.all()[0], context={'request': request})
    object_serialized = None
    if notification.notification_type == 'notification_post_sub':
        object_serialized = serializers.MinimalThreadSerializer(notification.notification_object).data

    for user in notification.notification_users.all():
        
        async_to_sync(get_channel_layer().group_send)(
            'notifications_%s' % request.user.id,
                {
                    "type": "notification",
                    "notification_data": {
                        "notification_type": notification.notification_type,
                        "notification_actor": actor_serializer.data,
                        "notification_object": object_serialized
                }
            }
        )