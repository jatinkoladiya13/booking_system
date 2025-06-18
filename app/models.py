from django.db import models
from django.contrib.auth.models import User

class FitnessClass(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    datetime = models.DateTimeField()
    instructor = models.CharField(max_length=100, blank=True, null=True)
    available_slots = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.name} on {self.datetime}"

class Booking(models.Model):
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)    