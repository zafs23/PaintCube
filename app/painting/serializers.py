from rest_framework import serializers

from core.models import Category, Supply, Painting


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


class PaintingSerializer(serializers.ModelSerializer):
    """Serializer for Painting objects"""
    # we need to define primary key related fields within the fields
    # as category and supplies are not part of the serializer they are
    # refering to category and supply models
    category = serializers.PrimaryKeyRelatedField(  # this will only include
        # the primary key (id) not the whole object
        many=True,
        queryset=Category.objects.all()
    )
    supply = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Supply.objects.all()
    )

    class Meta:
        model = Painting
        fields = ('id', 'title', 'painting_create_date', 'link_to_instragram',
                  'category', 'supply')
        read_only_fields = ('id',)  # the id will be read only field
