from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self) -> str:
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    roles = models.ManyToManyField(Role, related_name='users')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} profile"


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor')
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    tutor = models.ForeignKey(Tutor, on_delete=models.PROTECT, related_name='courses')
    price_cents = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['course', 'start_time']),
        ]

    def __str__(self) -> str:
        return f"{self.course.title} @ {self.start_time}"


class Availability(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='availability')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['tutor', 'start_time']),
        ]


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')


class Booking(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'session')


class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/', blank=True)
    url = models.URLField(blank=True)


class Payment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='payments')
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=10, default='usd')
    stripe_payment_intent = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=32, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

class SiteSetting(models.Model):
    name = models.CharField(max_length=64, default='default', unique=True)
    stripe_api_key = models.CharField(max_length=255, blank=True)
    stripe_webhook_secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Settings({self.name})"


class ActionRequest(models.Model):
    REQUEST_CANCEL_BOOKING = 'cancel_booking'
    REQUEST_TYPES = [
        (REQUEST_CANCEL_BOOKING, 'Cancel booking'),
    ]
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    request_type = models.CharField(max_length=64, choices=REQUEST_TYPES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='action_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='action_reviews')
    review_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'request_type']),
        ]


# Create your models here.
