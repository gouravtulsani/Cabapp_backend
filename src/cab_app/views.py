from rest_framework.permissions import (
    IsAuthenticated, 
    AllowAny
)
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.authtoken.models import Token 
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework import status
from .serializers import (
    RegisterSerializer,
    BookRideSerializer,
    CompleteRideSerializer
)
from .models import (
    Register,
    RideHistory
)
from .helper import (
    auth_login,
    auth_logout,
)

# constants
MAX_SEAT = 4
SHARING = '1'
PERSONAL = '2'
FREE = '3'

# Create your views here.

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def home(request):
    resp = {'home': 'welcome to cab app',
    'user_details': {
            'username': request.user.username,
            'active_user': request.user.is_active,
            'token': request.auth.key,
            'email': request.user.email,
        }
    }
    user = Register.objects.get(user_id=request.user)
    resp['user_details']['phone_number'] = user.phone_number
    resp['user_details']['full_name'] = user.first_name + ' ' + user.last_name

    if user.is_driver:
        resp['user_details']['car_model'] = user.car_model
        resp['user_details']['car_number'] = user.car_number

    return Response(resp, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    resp={}
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    user = authenticate(request, username=username, password=password)
    if user is None:
        resp["status"] = 'Unauthorized user'
        return Response(resp, status = status.HTTP_401_UNAUTHORIZED)

    if Token.objects.filter(user=user).exists():
        Token.objects.filter(user=user).delete()

    token = Token.objects.create(user=user)
    token.save()

    resp['status'] = 'login successfully'
    resp['token'] = token.key
    resp['username'] = token.user.username
    resp['is_superuser'] = token.user.is_superuser


    return Response(resp, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def logout(request):
    user=request.user

    if Token.objects.filter(user=user).exists():
        Token.objects.filter(user=user).delete()

    resp = {'status': 'logout'}

    return Response(resp, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
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
    if usr.booking_status != FREE:
        resp['status'] = 'Your ride is already in porgress, cannot book more than one cab at the same time'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    if not data['sharing']:
        driver_available = Register.objects.filter(Q(is_driver=True), Q(booking_status=FREE)).first()
        if not driver_available:
            resp['status'] = 'Sorry, No free driver available please try again'
            return Response(resp, status=status.HTTP_200_OK)

        r = RideHistory.objects.create(
            customer = usr,
            driver = driver_available,
            ride_from = data['ride_from'],
            ride_to = data['ride_to'],
            share=data['sharing']
        )
        r.save()
        resp['status'] = 'cab booked successfully'
        resp['driver_details'] = {
            'name': driver_available.user_id.username,
            'phone_number': driver_available.phone_number,
            'car_model': driver_available.car_model,
            'car_number': driver_available.car_number
        }
        driver_available.booking_status = PERSONAL
        driver_available.seats_booked = MAX_SEAT
        driver_available.save()
        usr.booking_status = PERSONAL
        usr.seats_booked = MAX_SEAT
        usr.save()
    else:
        drivers = Register.objects.filter(Q(is_driver=True),
            Q(booking_status=FREE) |
            Q(booking_status=SHARING)
        )

        for obj in drivers.order_by('-seats_booked'):
            if int(obj.seats_booked) + data['seats'] > MAX_SEAT:
                continue
            driver_available = obj
            break

        if driver_available:
            r = RideHistory.objects.create(
                customer = usr,
                driver = driver_available,
                ride_from = data['ride_from'],
                ride_to = data['ride_to'],
                share=data['sharing']
            )
            r.save()
            resp['status'] = 'cab booked successfully'
            resp['driver_details'] = {
                'name': driver_available.user_id.username,
                'phone_number': driver_available.phone_number,
                'car_model': driver_available.car_model,
                'car_number': driver_available.car_number
            }
            driver_available.booking_status = SHARING
            driver_available.seats_booked += data['seats']
            driver_available.save()
            usr.booking_status = SHARING
            usr.seats_booked = data['seats']
            usr.save()

    return Response(resp, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def complete_ride(request):
    resp={}

    serializer = CompleteRideSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer_name = serializer.validated_data['customer_name']

    driver = Register.objects.get(user_id=request.user.id)
    if not driver.is_driver:
        resp['status'] = 'Customer can not cancel ride, ask your driver to do that for you'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    customer_detail =  User.objects.filter(username=customer_name)
    if not customer_detail:
        resp['status'] = 'no such customer found'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)
    customer_detail = Register.objects.get(user_id=customer_detail[0])
    seats_booked_by_customer = customer_detail.seats_booked

    ride_detail = RideHistory.objects.filter(
        Q(driver_id=driver.id),
        Q(customer_id=customer_detail.id),
        Q(complete=False)
    )
    if not ride_detail:
        resp['status'] = 'No on going ride found'
        return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    ride_detail = ride_detail[0]
    ride_detail.complete = True
    ride_detail.save()
    customer = ride_detail.customer
    customer.booking_status = FREE
    customer.seats_booked = 0
    customer.save()

    if driver.seats_booked == seats_booked_by_customer:
        driver.booking_status = FREE
    else:
        driver.seats_booked -= seats_booked_by_customer 
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

    if request.user.is_superuser:
        data = RideHistory.objects.all()
    else:
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
