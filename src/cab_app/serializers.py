from rest_framework import serializers
from .validations import (
    validate_phone_number,
    validate_car_number
)
from django.contrib.auth import get_user_model
from django.db.models import Q

# CONSTANTS
MAX_SEATS_FOR_SHARE = 2

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=30)
    password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    email = serializers.EmailField(required=True, max_length=50)
    phone_number = serializers.CharField(required=True, max_length=10, validators=[validate_phone_number])
    is_driver = serializers.BooleanField(default=False)
    car_model = serializers.CharField(max_length = 20, min_length = 1, required=False)
    car_number = serializers.CharField(max_length = 20, min_length = 1, required=False, validators=[validate_car_number])

    def validate(self, data):
        errors = []
        if data['is_driver']:
            if 'car_model' not in data or 'car_number' not in data:
                errors.append('car_number and car_model both are required')
        else:
            if 'car_model' in data or 'car_number' in data:
                errors.append('car_number and car_model should not be present')


        user = User.objects.filter(
            Q(email=data['email']) |
            Q(username=data['username'])
        )
        if user.count() != 0:
            errors.append('This username/email already exists')

        if len(errors) != 0:
            raise serializers.ValidationError({'errors':errors})

        return data

class BookRideSerializer(serializers.Serializer):
    ride_from = serializers.CharField(required=True, max_length=30)
    ride_to = serializers.CharField(required=True, max_length=30)
    sharing = serializers.BooleanField(required=True)
    seats = serializers.IntegerField(required=False)

    def validate(self, data):
        errors = []
        if data['ride_from'] == data['ride_to']:
            errors.append('ride_from and ride_to can not be the same')

        if data['sharing']:
            if 'seats' not in data:
                errors.append('specify no. of seats 1 or 2.')
            else:
                if not 0 < data['seats'] <= MAX_SEATS_FOR_SHARE:
                    errors.append('InValid no. of seats expected 1 or 2')
        else:
            if 'seats' in data:
                errors.append('cannot specify no. of seats with personal ride.')
            else:
                data['seats'] = 4

        if len(errors) != 0:
            raise serializers.ValidationError({"errors": errors})

        return data

class CompleteRideSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=True, max_length=30)        