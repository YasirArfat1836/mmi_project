from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CourseViewSet,
    TutorViewSet,
    SessionViewSet,
    EnrollmentViewSet,
    BookingViewSet,
    ResourceViewSet,
    PaymentViewSet,
    create_checkout_session,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'tutors', TutorViewSet, basename='tutor')
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('payments/create-checkout-session/', create_checkout_session, name='create_checkout_session'),
]


