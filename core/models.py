from django.db import models
from django.contrib.auth.models import User

# 1. Profile: Farmer-specific details
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, unique=True)
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# 2. Tool: Equipment for rent
class Tool(models.Model):
    CATEGORY_CHOICES = [
        ('tractor', 'Tractor'),
        ('plow', 'Plow/Tillage'),
        ('harvester', 'Harvester'),
        ('irrigation', 'Irrigation Tools'),
        ('other', 'Other'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_tools')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='tool_images/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    available_from = models.DateField()
    available_to = models.DateField()

    def __str__(self):
        return self.name

# 3. Booking: The Rental Workflow
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('picked_up', 'Picked Up'),
        ('returned', 'Returned'),
    ]
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='bookings')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    delivery_requested = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    pickup_proof = models.ImageField(upload_to='proofs/', null=True, blank=True)
    return_proof = models.ImageField(upload_to='proofs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 4. Message: Chat logic
class Message(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# 5. Review: Trust and Ratings
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_left')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

# 6. Report: Handling Disputes (Required by your view)
class Report(models.Model):
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)