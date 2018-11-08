""" Custom Validations """
import re
from rest_framework.serializers import ValidationError
from django.db.models import Q
from .models import Register

PHONE_NO_REGEX = re.compile(r'^\d{10}$')
CAR_NO_REGEX = re.compile(r'^(([A-Za-z]){2}(-)(?:[0-9]){1,2}(-)(?:[A-Za-z]){2}(-)([0-9]){1,4})$')


def validate_phone_number(phone_number):
    if not PHONE_NO_REGEX.match(phone_number):
        raise ValidationError('InValid phone_number')
    if Register.objects.filter(phone_number=phone_number).count() != 0:
        raise ValidationError('phone_number already exists')


def validate_car_number(car_number):
    if not CAR_NO_REGEX.match(car_number):
        raise ValidationError('InValid car number')
    if Register.objects.filter(car_number=car_number).count() != 0:
        raise ValidationError('car number already exists')