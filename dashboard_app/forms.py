import re
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import EmailVerification
import re


# Create forms
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)

    # Define form meta
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ("username", "email", "password")

    # Clean method to validate username and email
    def clean_username(self):
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        return email

    # Clean method to validate password
    def clean_password(self):
        password = self.cleaned_data.get("password")
        regex = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d]{8,}$")

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")

        if not regex.match(password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter or one lowercase letter, one digit."
            )

        return password

    # Save method to create user
    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        user.is_active = False

        if commit:
            user.save()
            # Create EmailVerification instance for the new user
            EmailVerification.objects.create(user=user)

        return user


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
