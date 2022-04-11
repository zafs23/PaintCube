from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category, Supply, Painting

from painting import serializers


# as the category and supply viewset classes have so much in common
# it will be better to refactor the common fuctionality in a single
# class
class BasePaintingAttrViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin):
    """Common viewset for user owned painting attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object (category/supply)"""
        serializer.save(user=self.request.user)


class CategoryViewSet(BasePaintingAttrViewSet):
    """Manage category in the database"""
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class SupplyViewSet(BasePaintingAttrViewSet):
    """Manage supply in the database"""
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    queryset = Supply.objects.all()
    serializer_class = serializers.SupplySerializer


class PaintingViewSet(viewsets.ModelViewSet):
    """Manage painting in the databse"""
    serializer_class = serializers.PaintingSerializer
    queryset = Painting.objects.all()


    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return paintings for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user)
        # we do no tneed .order_by('-id')

    #override a serializer class after retrueve action and return detail
    # thus when the retrieve is called we are going to return the detail
    # serializer
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.PaintingDetailSerializer

        return self.serializer_class
# Create your views here.
# going to use list model fuction from the rest rest_framework
