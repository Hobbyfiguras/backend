from rest_framework import permissions
import guardian
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class BaseObjectPermissions(permissions.DjangoObjectPermissions):
    default_actions = [
        "create",
        "list",
        "retrieve",
        "update",
        "destroy",
        "partial_update"
    ]
    authenticated_users_only = False

    def has_permission(self, request, view):            # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
        not request.user.is_authenticated and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)

        if getattr(view, 'action'):
            if view.action in view.safe_actions:
                return True
            if not view.action in self.default_actions:
                return request.user.has_perms(view.action_perms_map[view.action])

        perms = self.get_required_permissions(request.method, queryset.model)

        return request.user.has_perms(perms)

    def has_object_permission(self, request, view, obj):
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)
        is_action_safe = False
        # Check if the user also has action permissions:
        if view.safe_actions:
            if view.action in view.safe_actions:
                is_action_safe = True
        
        if view.action:
            if not view.action in self.default_actions and not is_action_safe:
                if not user.has_perms(view.action_perms_map[view.action], obj):
                    # If the user does not have permissions we need to determine if
                    # they have read permissions to see 403, or not, and simply see
                    # a 404 response.

                    if request.method in SAFE_METHODS:
                        # Read permissions already checked and failed, no need
                        # to make another lookup.
                        raise Http404

                    read_perms = self.get_required_object_permissions('GET', model_cls)
                    if not user.has_perms(read_perms, obj):
                        raise Http404

                    # Has read permissions.
                    return False
        if not user.has_perms(perms, obj) and view.action in self.default_actions:
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not user.has_perms(read_perms, obj):
                raise Http404

            # Has read permissions.
            return False
        return True