import re
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import EmailVerification
import re
from django.contrib.auth.hashers import check_password
from .models import UploadCsvFile


# Create forms for user registration
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

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


# Create forms for user login
class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)


class ChangePassword(forms.Form):
    new_password = forms.CharField(required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ChangePassword, self).__init__(*args, **kwargs)

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password


class ChangeEmail(forms.Form):
    new_email = forms.EmailField(required=True)
    confirm_email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(ChangeEmail, self).__init__(*args, **kwargs)

    def clean_confirm_email(self):
        new_email = self.cleaned_data.get("new_email")
        confirm_email = self.cleaned_data.get("confirm_email")
        if new_email != confirm_email:
            raise forms.ValidationError("Emails do not match")
        return confirm_email


class CsvFileForm(forms.ModelForm):
    class Meta:
        model = UploadCsvFile
        fields = ("file",)

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.name.endswith(".csv"):
                return file
            else:
                raise forms.ValidationError("File is not a CSV file")
        else:
            raise forms.ValidationError("File is not a CSV file")


class RecoverPassword(forms.Form):
    username = forms.CharField(required=True)
    new_password = forms.CharField(required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(RecoverPassword, self).__init__(*args, **kwargs)

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password
