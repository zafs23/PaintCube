from rest_framework import serializers

from core.models import Category, Supply


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category objects"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)  # the id will be read only field


class SupplySerializer(serializers.ModelSerializer):
    """Serializer for Supply objects"""

    class Meta:
        model = Supply
        fields = ('id', 'name')
        read_only_fields = ('id',)  # the id will be read only field
