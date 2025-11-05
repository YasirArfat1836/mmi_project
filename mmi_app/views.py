from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Course, Enrollment, Session, Booking, Resource, Tutor, Payment, ActionRequest
from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    SessionSerializer,
    BookingSerializer,
    ResourceSerializer,
    TutorSerializer,
    PaymentSerializer,
)
from .forms import RegisterForm, EnrollmentForm, BookingForm, ProfileForm, ProfileDetailsForm
from .utils import get_stripe_keys


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('tutor__user').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


class TutorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tutor.objects.select_related('user').all()
    serializer_class = TutorSerializer
    permission_classes = [permissions.AllowAny]


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Session.objects.select_related('course').all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.AllowAny]


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(student=self.request.user).select_related('session__course')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.select_related('course').all()
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(enrollment__student=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_API_KEY
    enrollment_id = request.data.get('enrollment_id')
    amount_cents = int(request.data.get('amount_cents', 0))
    currency = request.data.get('currency', 'usd')
    if not enrollment_id or amount_cents <= 0:
        return Response({'detail': 'Invalid payload'}, status=400)
    # Placeholder: in real flow, create Stripe Checkout Session and persist Payment
    return Response({'status': 'ok', 'message': 'Stripe integration pending configuration'})


# Page views (server-rendered templates)
def home_page(request):
    courses = Course.objects.select_related('tutor__user').filter(is_active=True)[:6]
    return render(request, 'pages/index.html', { 'courses': courses })


def courses_page(request):
    courses = Course.objects.select_related('tutor__user').filter(is_active=True)
    return render(request, 'pages/courses.html', { 'courses': courses })


def course_detail_page(request, slug: str):
    course = get_object_or_404(Course.objects.select_related('tutor__user'), slug=slug, is_active=True)
    sessions = course.sessions.order_by('start_time')
    resources = course.resources.all()
    return render(request, 'pages/course_detail.html', { 'course': course, 'sessions': sessions, 'resources': resources })


def tutors_page(request):
    tutors = Tutor.objects.select_related('user').all()
    return render(request, 'pages/tutors.html', { 'tutors': tutors })


def dashboard_page(request):
    if not request.user.is_authenticated:
        return render(request, 'pages/dashboard_anon.html', status=401)
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course__tutor__user')
    bookings = list(Booking.objects.filter(student=request.user).select_related('session__course'))
    paid_enrollment_ids = set(Payment.objects.filter(enrollment__student=request.user, status='paid').values_list('enrollment_id', flat=True))
    # Build map: booking_id -> latest status
    booking_status_map = {}
    for ar in ActionRequest.objects.filter(requested_by=request.user, booking__in=bookings).order_by('created_at'):
        booking_status_map[ar.booking_id] = ar.status
    # attach status to each booking for easy template rendering
    for b in bookings:
        setattr(b, 'request_status', booking_status_map.get(b.id))
    requests_all = ActionRequest.objects.filter(requested_by=request.user).select_related('booking__session__course').order_by('-created_at')[:25]
    return render(request, 'pages/dashboard.html', { 'enrollments': enrollments, 'bookings': bookings, 'paid_enrollment_ids': paid_enrollment_ids, 'requests_all': requests_all })


def bookings_page(request):
    sessions = Session.objects.select_related('course').order_by('start_time')[:50]
    return render(request, 'pages/bookings.html', { 'sessions': sessions })


def checkout_page(request):
    enrollment_id = request.GET.get('enrollment_id') or request.POST.get('enrollment_id')
    api_key, _ = get_stripe_keys()
    if request.method == 'POST' and api_key and enrollment_id:
        stripe.api_key = api_key
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        price_cents = max(0, int(enrollment.course.price_cents or 0))
        if price_cents <= 0:
            messages.info(request, 'This course is free. No payment required.')
            return redirect('dashboard')
        session = stripe.checkout.Session.create(
            mode='payment',
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': { 'name': enrollment.course.title },
                    'unit_amount': price_cents,
                },
                'quantity': 1,
            }],
            metadata={ 'enrollment_id': str(enrollment.id) },
            success_url=request.build_absolute_uri('/checkout/success/'),
            cancel_url=request.build_absolute_uri(f'/checkout/cancel/?enrollment_id={enrollment.id}'),
        )
        return redirect(session.url)
    return render(request, 'pages/checkout.html', { 'enrollment_id': enrollment_id, 'stripe_enabled': bool(api_key) })


def privacy_page(request):
    return render(request, 'pages/privacy.html')


def terms_page(request):
    return render(request, 'pages/terms.html')


def contact_page(request):
    return render(request, 'pages/contact.html')


def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created. Please sign in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'pages/register.html', { 'form': form })


@login_required
@require_POST
def enroll_action(request, slug: str):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    try:
        Enrollment.objects.get_or_create(student=request.user, course=course)
        messages.success(request, 'Enrolled successfully.')
    except Exception:
        messages.error(request, 'Could not enroll. Please try again.')
    return redirect('course-detail', slug=slug)


@login_required
@require_POST
def book_session_action(request, session_id: int):
    session = get_object_or_404(Session, id=session_id)
    current_bookings = session.bookings.count()
    if current_bookings >= session.capacity:
        messages.error(request, 'Session is full.')
        return redirect('bookings')
    Booking.objects.get_or_create(student=request.user, session=session)
    messages.success(request, 'Session booked.')
    return redirect('dashboard')


@login_required
def pay_enrollment_action(request, enrollment_id: int):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    amount_cents = enrollment.course.price_cents
    if not amount_cents or amount_cents <= 0:
        messages.info(request, 'This course is free. No payment required.')
        return redirect('dashboard')
    # Mock payment (sample) – Stripe integration planned for future
    Payment.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            'amount_cents': amount_cents,
            'currency': 'usd',
            'stripe_payment_intent': f'mock_{enrollment.id}',
            'status': 'paid',
        }
    )
    messages.success(request, 'Payment recorded (sample). Stripe integration coming soon.')
    return redirect('dashboard')


@login_required
@require_POST
def cancel_booking_action(request, booking_id: int):
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)
    # Create approval request instead of immediate cancel
    ActionRequest.objects.get_or_create(
        request_type=ActionRequest.REQUEST_CANCEL_BOOKING,
        booking=booking,
        requested_by=request.user,
        defaults={}
    )
    messages.info(request, 'Cancellation request submitted. Awaiting admin approval.')
    return redirect('dashboard')


@login_required
def profile_page(request):
    # ensure profile exists
    profile = getattr(request.user, 'profile', None)
    if profile is None:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST':
        user_form = ProfileForm(request.POST, instance=request.user)
        details_form = ProfileDetailsForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and details_form.is_valid():
            user_form.save()
            details_form.save()
            messages.success(request, 'Profile updated.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = ProfileForm(instance=request.user)
        details_form = ProfileDetailsForm(instance=profile)
    return render(request, 'pages/profile.html', { 'user_form': user_form, 'details_form': details_form, 'profile': profile })


@login_required
def admin_dashboard_page(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    metrics = {
        'users': request.user.__class__.objects.count(),
        'tutors': Tutor.objects.count(),
        'courses': Course.objects.count(),
        'sessions': Session.objects.count(),
        'enrollments': Enrollment.objects.count(),
        'bookings': Booking.objects.count(),
        'payments': Payment.objects.count(),
    }
    admin_links = [
        ('Users', '/admin/auth/user/'),
        ('Tutors', '/admin/mmi_app/tutor/'),
        ('Courses', '/admin/mmi_app/course/'),
        ('Sessions', '/admin/mmi_app/session/'),
        ('Enrollments', '/admin/mmi_app/enrollment/'),
        ('Bookings', '/admin/mmi_app/booking/'),
        ('Resources', '/admin/mmi_app/resource/'),
        ('Payments', '/admin/mmi_app/payment/'),
        ('Site settings', '/admin/mmi_app/sitesetting/'),
    ]
    # Admin-only datasets
    pending_requests = ActionRequest.objects.filter(status=ActionRequest.STATUS_PENDING).select_related('booking__session__course', 'requested_by').order_by('-created_at')[:10]
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-created_at')[:10]
    recent_bookings = Booking.objects.select_related('student', 'session__course').order_by('-created_at')[:10]
    recent_payments = Payment.objects.select_related('enrollment__student', 'enrollment__course').order_by('-created_at')[:10]

    context = {
        'metrics': metrics,
        'admin_links': admin_links,
        'pending_requests': pending_requests,
        'recent_enrollments': recent_enrollments,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
    }
    return render(request, 'pages/admin_dashboard.html', context)


@login_required
def logout_confirm_page(request):
    return render(request, 'pages/logout_confirm.html')


@login_required
@require_POST
def logout_perform(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('home')

# Create your views here.
