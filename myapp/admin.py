from django.contrib import admin
from .models import TestBooking , ContactMessage , UserProfile


admin.site.register(TestBooking)  # Register the model(s)
admin.site.register(ContactMessage)  # Register the model(s)
admin.site.register(UserProfile)  # Register UserProfile model
