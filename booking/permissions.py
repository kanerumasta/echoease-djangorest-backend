from rest_framework import permissions

class IsInvolved(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj.artist.user == request.user or obj.client == request.user)
        return obj.artist.user == request.user or obj.client == request.user