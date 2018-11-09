from django.urls import path

from . import views

urlpatterns = [
	path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('book_ride', views.book_ride, name='book_ride'),
    path('get_ride_history', views.get_ride_history, name='get_ride_history'),
    path('complete_ride', views.complete_ride, name='complete_ride'),
]
