from django import forms
from django.contrib.auth.models import User
from .models import Enrollment, Booking, UserProfile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match')
        return cleaned


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = []


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = []


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone']


