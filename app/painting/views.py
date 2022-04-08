from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category

from painting import serializers


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage category in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):  # any filtering can be applied here
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
# Create your views here.
# going to use list model fuction from the rest rest_framework
