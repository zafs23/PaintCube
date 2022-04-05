from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
# helps with trasnsition from one language to the correct one

from rest_framework import serializers


# specify fields that we want from the module
class UserSerializer(serializers.ModelSerializer):
    """serializer for the users object"""

    class Meta:
        model = get_user_model()  # base of the model serializer
        # specify fields to be included in the serializer, the fields will be
        # converted to and from JSon when we make the HTTP POST
        fields = ('email', 'password', 'name')
        # extra keyword: confgure extra setting, to ensure the password is
        # write_only
        # and minimum requirement is 8 characters
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):  # override funcitons
        """create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)  # use
        # the ** to unwind the validated data into parameters
        # the validated data will contain all data that was passed into the
        # the serializer(JSON data) and we will use that to create our user

    def update(self, instance, validated_data):
        """update a user, setting the password correctly, and return it"""
        # remove the password from the dictionary
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


# new serializer based off the Django standard serializer
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False  # django by default trim whitespace, we don't
        # want that for checking the password
    )

    def validate(self, attrs):
        # attrs are the attributes we are going to validate
        """validate and authenticate the user"""
        # have to check that the email and password is a char field
        # passing the fields we want to validate using this attrs
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),  # access context of request
            username=email,  # changing django default to accepting
            # email address as username
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            # the underscore helps to change the language later if needed
            raise serializers.ValidationError(msg, code='authentication')
            # passes errors as 400

        attrs['user'] = user
        return attrs  # as overriding the validate function must return then
        # values at the end when validation is successful
