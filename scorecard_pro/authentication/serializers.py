from rest_framework import serializers
from .models import CustomUser
import re

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'mobile', 'email', 'password', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])  # Hash password
        user.save()
        return user


from rest_framework import serializers
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

mobile_number_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Mobile number must be entered in the format: '9999999999'. only 10 digits allowed."
)  


def validate_password(password):
    if not 8 <= len(password) <= 15:
        raise ValidationError(_('Password must be between 8 and 20 characters long.'), code='password_length')

    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
    if not re.match(password_regex, password):
        raise ValidationError(_('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character.'), code='password_complexity')


class UserSignupValidator(serializers.Serializer):
    full_name = serializers.CharField(max_length=100, required=True, allow_blank=False, error_messages={
        'required': 'Full Name is required',
        'blank': 'Full Name cannot be empty',
    })
    mobile = serializers.CharField(required=True, allow_blank=False, validators=[mobile_number_validator], error_messages={
        'required': 'Mobile Number is required',
        'blank': 'Mobile Number cannot be empty',
    })
    email = serializers.EmailField(required=True, allow_blank=False, error_messages={
        'required': 'Email is required',
        'blank': 'Email cannot be empty',
    })
    password = serializers.CharField(write_only=True, required=True, allow_blank=False, validators=[validate_password], error_messages={
        'required': 'Password is required',
        'blank': 'Password cannot be empty',
    })
    # user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True, error_messages={
    #     'required': 'User Type is required',
    # })


class UserLoginValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, error_messages={
        'required': 'Email is required',
        'blank': 'Email cannot be empty',
    })
    password = serializers.CharField(max_length=20, required=True, allow_blank=False, error_messages={
        'required': 'Password is required',
        'blank': 'Password cannot be empty',
    })
