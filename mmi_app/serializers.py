from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Course, Enrollment, Session, Booking, Resource, Tutor, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class TutorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Tutor
        fields = ['id', 'user', 'bio']


class CourseSerializer(serializers.ModelSerializer):
    tutor = TutorSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'tutor', 'price_cents', 'is_active']


class SessionSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'course', 'start_time', 'end_time', 'capacity']


class EnrollmentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'created_at']
        read_only_fields = ['created_at']


class BookingSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'session', 'created_at']
        read_only_fields = ['created_at']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'course', 'title', 'file', 'url']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'enrollment', 'amount_cents', 'currency', 'stripe_payment_intent', 'status', 'created_at']
        read_only_fields = ['created_at']


