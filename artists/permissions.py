from rest_framework import permissions


# class IsVerifiedUser(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_verified

class IsArtist(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'is_artist') and request.user.is_artist