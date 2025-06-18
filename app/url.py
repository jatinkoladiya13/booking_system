from django.urls import path, include
from app import views

urlpatterns = [
    path('api/user/register/', views.register),
    path('api/user/login/',views.login),
    path('api/user/get/', views.get_user),

    path('api/fittnessClass/create/',views.create_fitness_class), 
    path('api/fittnessClass/get/',views.get_fitness_class),
    path('api/booking/book/', views.book_class),
    path('api/bookings/get/',views.get_bookings),
]