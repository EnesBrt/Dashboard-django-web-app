from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage, send_mail
from django.urls import reverse
from .models import EmailVerification
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import uuid


# signup function to handle user signup and email verification process
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            # Retrieve the email verification object
            email_verification = EmailVerification.objects.get(user=user)
            token = email_verification.verification_token

            # Construct activation URL
            activation_url = request.build_absolute_uri(
                reverse("activate_account", args=[token])
            )

            # Construct and send the email
            email_subject = "Activate Your Account"
            email_body = f"Hi {user.username},\n\nPlease click the following link to activate your account: {activation_url}\n\nThank You!"

            email = EmailMessage(email_subject, email_body, to=[user.email])
            email.send()

            return redirect("confirmation_sent")

    else:
        form = CustomUserCreationForm()

    return render(request, "signup.html", {"form": form})


# activate_account function to handle account activation process and redirection to a success or failure page
# depending on the verification status of the user account
def activate_account(request, token):
    # Retrieve the email verification object
    try:
        email_verification = EmailVerification.objects.get(verification_token=token)

        # Check if the token has expired
        if email_verification.is_token_expired:
            # Token expired
            return redirect("activation_failed")

        # Check if the user has already been activated
        if not email_verification.verified:
            # Activate the account
            user = email_verification.user
            user.is_active = True
            user.save()

            email_verification.verified = True
            email_verification.save()

            return redirect("activation_success")  # Redirect to a success page

    # Handle the case where the email verification object does not exist
    except ObjectDoesNotExist:
        # Invalid token
        return redirect("activation_failed")  # Redirect to a page indicating failure

    return redirect("home")  # General redirect if none of the above conditions met


def resent_activation_email(request, user_id):
    try:
        # Retrieve the user object and email verification object based on the user ID provided in the URL parameters
        user = User.objects.get(id=user_id)
        email_verification = EmailVerification.objects.get(user=user)

        # Generate new token and reset expiration
        email_verification.verification_token = uuid.uuid4()
        email_verification.save()

        # Construct activation URL
        activation_url = request.build_absolute_uri(
            reverse("activate_account", args=[email_verification.verification_token])
        )

        # Construct and send the email
        email_subject = "Activate Your Account"
        email_body = f"Hi {user.username},\n\nPlease click the following link to activate your account: {activation_url}\n\nThank You!"

        email = EmailMessage(email_subject, email_body, to=[user.email])
        email.send()

        return redirect("email_resent_success")  # Redirect to a page indicating success

    except User.DoesNotExist:
        return redirect("email_resent_failed")  # Redirect to a page indicating failure

    return redirect("home")  # General redirect if none of the above conditions met


# Login function view
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("dashboard")

            else:
                form.add_error(None, "Invalid username or password")

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


# Logout function view
def logout_view(request):
    return render(request, "logout.html")


# Dashboard function view
def dashboard(request):
    return render(request, "dashboard.html")
