from rest_framework import serializers, fields

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
    painting_create_date = fields.DateField(input_formats=['%Y-%m-%d'])
    # we need to define primary key related fields within the fields
    # as category and supplies are not part of the serializer they are
    # refering to category and supply models
    categories = serializers.PrimaryKeyRelatedField(  # this will only include
        # the primary key (id) not the whole object
        many=True,
        queryset=Category.objects.all()
    )
    supplies = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Supply.objects.all()
    )

    class Meta:
        model = Painting
        fields = ('id', 'title', 'painting_create_date', 'link_to_instragram',
                  'categories', 'supplies')
        read_only_fields = ('id',)  # the id will be read only field


class PaintingDetailSerializer(PaintingSerializer):
    """Serialize a painting in detail using the base painting serializer"""
    categories = CategorySerializer(many=True, read_only=True)
    supplies = SupplySerializer(many=True, read_only=True)
    # using the category and supply serializer we can show the name and id of
    # these objects


class PaintingImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images of the paintings"""

    class Meta:
        model = Painting
        fields = ('id', 'image')
        read_only_fields = ('id',)
