from django.contrib import admin
from app.models import FitnessClass, Booking
# Register your models here.

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    model = FitnessClass
    list_display = ['id', 'name', 'instructor', 'available_slots', 'datetime']
    ordering = ['pk']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = ['id', 'user', 'fitness_class', 'booked_at', ]
    ordering = ['pk']