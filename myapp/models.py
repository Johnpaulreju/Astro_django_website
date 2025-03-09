import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


def generate_unique_id():
    """Generate a 4-character alphanumeric ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    phone = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number
    address = models.TextField(blank=True, null=True)  # Optional address
    is_admin = models.BooleanField(default=False)  # Flag for admin users
    unique_id = models.CharField(max_length=4, unique=True, default=generate_unique_id, editable=False)  # ✅ Renamed field

    def __str__(self):
        return f"{self.user.username} ({self.unique_id})"


class TestBooking(models.Model):
    TEST_STAGES = [
        ('upcoming', 'Upcoming'),
        ('sample_collected', 'Sample Collected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('report_ready', 'Report Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=100)
    date = models.DateField()
    test_type = models.TextField()  # Store multiple test names
    hour = models.CharField(max_length=50)
    total_price = models.IntegerField(default=0)  # Store total price
    booked_by = models.CharField(max_length=100, default="Unknown")  # Username of the person who booked
    booked_on = models.DateTimeField(default=now)  # Auto store booking date & time
    labreport = models.FileField(upload_to='lab_reports/', null=True, blank=True)  # Store PDF reports
    stage = models.CharField(max_length=20, choices=TEST_STAGES, default='upcoming')  # Test stage tracking

    def __str__(self):
        return f"{self.name} - {self.test_type} - ₹{self.total_price} - Stage: {self.stage}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
