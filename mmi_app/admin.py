from django.contrib import admin
from .models import Role, UserProfile, Tutor, Course, Session, Availability, Enrollment, Booking, Resource, Payment, SiteSetting, ActionRequest
from django.contrib import messages
from django.utils import timezone


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


@admin.register(ActionRequest)
class ActionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_type', 'status', 'requested_by', 'booking', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('request_type', 'status')
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='Approve selected requests')
    def approve_requests(self, request, queryset):
        approved = 0
        for ar in queryset.only('id', 'status', 'request_type', 'booking_id'):
            if ar.status != 'pending':
                continue
            if ar.request_type == 'cancel_booking' and ar.booking_id:
                try:
                    # Delete booking by ID to avoid touching unsaved related instances
                    from .models import Booking
                    Booking.objects.filter(id=ar.booking_id).delete()
                except Exception:
                    pass
            # Update the ActionRequest row directly
            type(self).model.objects.filter(id=ar.id).update(
                status='approved', reviewed_by=request.user.id, reviewed_at=timezone.now()
            )
            approved += 1
        self.message_user(request, f"Approved {approved} request(s).", level=messages.SUCCESS)

    @admin.action(description='Reject selected requests')
    def reject_requests(self, request, queryset):
        pending_ids = list(queryset.filter(status='pending').values_list('id', flat=True))
        if pending_ids:
            type(self).model.objects.filter(id__in=pending_ids).update(
                status='rejected', reviewed_by=request.user.id, reviewed_at=timezone.now()
            )
        self.message_user(request, f"Rejected {len(pending_ids)} request(s).", level=messages.WARNING)

# Register your models here.
