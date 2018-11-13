from django.db import models
from django.contrib.auth.models import User

# Create your models here.
OPTION_CHOICES = [(1, 'sharing'), (2, 'personal'), (3, 'free')]

class Register(models.Model):
	"""This is a user register
	where we store all the details of the customer and driver"""
	user_id = models.OneToOneField(User, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	email = models.EmailField(max_length=50, unique=True)
	phone_number = models.CharField(max_length=10, unique=True)
	is_driver = models.BooleanField(default=False)
	car_model = models.CharField(max_length=20)
	car_number = models.CharField(max_length=10)
	booking_status = models.CharField(max_length=8, choices=OPTION_CHOICES, default=3)
	seats_booked = models.IntegerField(default=0)

	def __str__(self):
		return "%s" % (self.user_id.username)


class RideHistory(models.Model):
	"""this model store the history of each and every ride
	booked by any of the customer"""
	ride_id = models.AutoField(primary_key=True)
	customer = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='customer')
	driver = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='driver')
	ride_from = models.CharField(max_length=60)
	ride_to = models.CharField(max_length=60)
	ride_time = models.DateTimeField(auto_now_add=True, editable=False)
	complete = models.BooleanField(default=False)
	share = models.BooleanField(default=False)


	def __str__(self):
		return "id: %s, customer: %s, driver: %s, time: %s" % (self.ride_id, self.customer, self.driver, self.ride_time)
