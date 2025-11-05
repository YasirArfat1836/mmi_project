from django.contrib import admin
from .models import Role, UserProfile, Tutor, Course, Session, Availability, Enrollment, Booking, Resource, Payment, SiteSetting


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone')
    filter_horizontal = ('roles',)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'tutor', 'price_cents', 'is_active')
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'start_time', 'end_time', 'capacity')
    list_filter = ('course',)


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'tutor', 'start_time', 'end_time')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'created_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'session', 'created_at')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'amount_cents', 'currency', 'status', 'created_at')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    fieldsets = (
        (None, { 'fields': ('name', 'is_active') }),
        ('Stripe', { 'fields': ('stripe_api_key', 'stripe_webhook_secret') }),
    )

    def has_add_permission(self, request):
        # limit to one active row; allow add if none exists
        if SiteSetting.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

# Register your models here.
