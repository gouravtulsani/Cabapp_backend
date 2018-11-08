from rest_framework.permissions import (
    IsAuthenticated, 
    AllowAny
)
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework import status
from .serializers import (
    RegisterSerializer,
    BookRideSerializer
)
from .models import (
    Register,
    RideHistory
)

# Create your views here.


@api_view(['POST'])
def register(request):
    resp={}

    # ==== Validate input ====

    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    u = User.objects.create_user(username = data["username"],
        password=data["password"],
        email=data["email"]
    )
    u.save()

    if data['is_driver']:
        d = Register.objects.create(user_id=User.objects.get(username=data['username']),
            first_name=data['first_name'], last_name=data['last_name'],
            email=data['email'], phone_number=data['phone_number'],
            car_model=data['car_model'], car_number=data['car_number'],
            is_driver=data['is_driver']
        )
        d.save()
        resp['status'] = 'Driver registered successfully'
    else:
        c = Register.objects.create(user_id=User.objects.get(username=data['username']),
            first_name=data['first_name'], last_name=data['last_name'],
            email=data['email'], phone_number=data['phone_number'],
            is_driver=data['is_driver']
        )
        c.save()
        resp['status'] = 'Customer registered successfully'

    return Response(resp, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def book_ride(request):
    resp={}

    # ==== Validate input ====

    serializer = BookRideSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    usr = Register.objects.get(user_id=request.user.id)
    if usr.is_driver:
        resp['status'] = 'Driver can not book a cab, register yourself as customer'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)
    if usr.busy:
        resp['status'] = 'Your ride is already in porgress, cannot book more than one cab at the same time'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    driver_available = Register.objects.filter(is_driver=True).filter(busy=False).first()
    if not driver_available:
        resp['status'] = 'Sorry, No free driver available please try again'
        return Response(resp, status=status.HTTP_200_OK)

    r = RideHistory.objects.create(
        customer = usr,
        driver = driver_available,
        ride_from = data['ride_from'],
        ride_to = data['ride_to']
    )
    r.save()
    resp['status'] = 'cab booked successfully'
    resp['driver_details'] = {
        'name': driver_available.user_id.username,
        'phone_number': driver_available.phone_number,
        'car_model': driver_available.car_model,
        'car_number': driver_available.car_number
    }
    driver_available.busy = True
    driver_available.save()
    usr.busy = True
    usr.save()

    return Response(resp, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def complete_ride(request):
    resp={}

    driver = Register.objects.get(user_id=request.user.id)
    if not driver.is_driver:
        resp['status'] = 'Customer can not cancel ride, ask your driver to do that for you'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    ride_detail = RideHistory.objects.filter(driver=driver).filter(complete=False).first()
    if not ride_detail:
        resp['status'] = 'No on going ride found'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    ride_detail.complete = True
    ride_detail.save()
    customer = ride_detail.customer
    customer.busy = False
    customer.save()
    driver.busy = False
    driver.save()
    resp['status'] = 'ride completed successfully'
    resp['ride_detail'] = {
        'from': ride_detail.ride_from,
        'to': ride_detail.ride_to,
        'customer': customer.user_id.username
    }

    return Response(resp, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_ride_history(request):
    resp = []
    req_user = Register.objects.get(user_id=request.user)

    data = RideHistory.objects.filter(
        Q(customer_id=req_user.id) |
        Q(driver_id=req_user.id)
    )
    resp = [{
        'id': index+1,
        'ride_from': row.ride_from, 
        'ride_to': row.ride_to, 
        'ride_time': row.ride_time,
        'complete': row.complete
    } for index, row in enumerate(data)]

    return Response(resp, status=status.HTTP_200_OK)
