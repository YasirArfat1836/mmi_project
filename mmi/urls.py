"""
URL configuration for mmi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView
from mmi_app import views as page_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', page_views.home_page, name='home'),
    path('courses/', page_views.courses_page, name='courses'),
    path('courses/<slug:slug>/', page_views.course_detail_page, name='course-detail'),
    path('tutors/', page_views.tutors_page, name='tutors'),
    path('dashboard/', page_views.dashboard_page, name='dashboard'),
    path('bookings/', page_views.bookings_page, name='bookings'),
    path('checkout/', page_views.checkout_page, name='checkout'),
    path('checkout/success/', TemplateView.as_view(template_name='pages/checkout_success.html'), name='checkout-success'),
    path('checkout/cancel/', TemplateView.as_view(template_name='pages/checkout_cancel.html'), name='checkout-cancel'),
    path('privacy/', page_views.privacy_page, name='privacy'),
    path('terms/', page_views.terms_page, name='terms'),
    path('contact/', page_views.contact_page, name='contact'),
    path('profile/', page_views.profile_page, name='profile'),
    path('admin-dashboard/', page_views.admin_dashboard_page, name='admin-dashboard'),
    # Auth pages
    path('auth/login/', auth_views.LoginView.as_view(template_name='pages/login.html'), name='login'),
    # Logout confirmation flow
    path('auth/logout/confirm/', page_views.logout_confirm_page, name='logout-confirm'),
    path('auth/logout/perform/', page_views.logout_perform, name='logout-perform'),
    path('auth/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('auth/register/', page_views.register_page, name='register'),
    # Actions
    path('enroll/<slug:slug>/', page_views.enroll_action, name='enroll'),
    path('book/<int:session_id>/', page_views.book_session_action, name='book-session'),
    path('pay/<int:enrollment_id>/', page_views.pay_enrollment_action, name='pay-enrollment'),
    path('cancel-booking/<int:booking_id>/', page_views.cancel_booking_action, name='cancel-booking'),
    path('admin/', admin.site.urls),
    path('api/', include('mmi_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
