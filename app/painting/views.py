from rest_framework.decorators import action  # for custom actions
from rest_framework.response import Response
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
        # to add the filtering for geting categories and supplies
        # depending on the painting we have to change the filter here
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )  # convert query parameter to integers and then to a boolean
        # we have assign a value here otherwise it'll convert it to a none type
        # the assigned only value will be 0 or 1
        # the query get parameter cant detect string or int
        # here assigned 0 is a default value, if passed it will be override
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(painting__isnull=False)

        return queryset.filter(
            user=self.request.user
            ).order_by('-name').distinct()
        # here we have to add distinct in the end otherwise django will return
        # duplicate items
        # return self.queryset.filter(user=self.request.user).order_by('-name')

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

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        # qs = '1,2,3'
        # converted_string = ['1','2','3']
        # returnd_list = [1, 2, 3]
        return [int(str_id) for str_id in qs.split(',')]  # qs is the comma
        # seperated list and we change the list items to integers

    def get_queryset(self):
        """Return paintings for the current authenticated user only"""
        # add filtering
        # request has a query params in a dictionary
        categories = self.request.query_params.get('categories')
        supplies = self.request.query_params.get('supplies')
        queryset = self.queryset  # get the queryset and the apply the filters
        # this filter helps to get painting depending on the categories and
        # supplies
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)
            # double underscore is convention for filtering foreign key objects
            # __in is a function whihc returns all the category ids that is
            # in the list that we provide
        if supplies:
            supply_ids = self._params_to_ints(supplies)
            queryset = queryset.filter(supplies__id__in=supply_ids)

        return queryset.filter(user=self.request.user)
        # we do not need .order_by('-id')

    # override a serializer class after retrueve action and return detail
    # thus when the retrieve is called we are going to return the detail
    # serializer
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.PaintingDetailSerializer
        elif self.action == 'upload_image':
            return serializers.PaintingImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new painting object"""
        serializer.save(user=self.request.user)
# Create your views here.
# going to use list model fuction from the rest rest_framework

    # the actions could be POST, PUT or PATCH
    # detail URL

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):  # passed in with the URL as pk
        """Upload an image of a painting"""
        painting = self.get_object()
        serializer = self.get_serializer(
            painting,
            data=request.data
        )

        if serializer.is_valid():  # check the serializer is valid
            serializer.save()  # save on the painting model with updated data
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(  # if not valid return errors
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
