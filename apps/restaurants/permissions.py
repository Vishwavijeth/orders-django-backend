from rest_framework import permissions

class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):
    # only owners can modify, rest can only view/read

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
    
class IsRestaurantAdmin(permissions.BasePermission):
    # users with restaurant_admin role

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.RESTAURANT_ADMIN
        )
    

class IsRestaurantAdmin(permissions.BasePermission):
    # Allows access only to restaurant admins.

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == request.user.Role.RESTAURANT_ADMIN
        )


class IsMenuOwnerOrReadOnly(permissions.BasePermission):
    # Read → anyone, Write → only restaurant owner

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.restaurant.owner_id == request.user.id