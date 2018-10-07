
from . import serializers

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification(request, notification):
    actor_serializer = serializers.PublicUserSerializer(notification.actor, context={'request': request})
    object_serialized = None
    if notification.notification_type == 'notification_post_sub':
        object_serialized = serializers.NotificationPostSerializer(notification.notification_object).data        
    async_to_sync(get_channel_layer().group_send)(
        'notifications_%s' % notification.user.id,
            {
                "type": "notification",
                "notification_data": {
                    "notification_type": notification.notification_type,
                    "actor": actor_serializer.data,
                    "notification_object": object_serialized
            }
        }
    )