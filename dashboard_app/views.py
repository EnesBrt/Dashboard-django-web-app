from django.shortcuts import render, redirect
from django.shortcuts import render
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
from django.contrib.auth.models import User
from .forms import ChangePassword
from .forms import ChangeEmail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UploadCsvFile
import pandas as pd
from .forms import CsvFileForm
import json
import os
from django.conf import settings
from .forms import RecoverPassword
from django.contrib.auth.hashers import make_password


# signup function to handle user signup and email verification process
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

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
    try:
        # Retrieve the email verification object
        email_verification = EmailVerification.objects.get(verification_token=token)

        # Check if the token has expired
        if email_verification.is_token_expired:
            # Token expired
            return render(request, "activation_failure.html")

        # Check if the user has already been activated
        if not email_verification.verified:
            # Activate the account
            user = email_verification.user
            user.is_active = True
            user.save()

            email_verification.verified = True
            email_verification.save()

            EmailVerification.objects.filter(user=user).exclude(
                id=email_verification.id
            ).delete()

            return redirect("activation_success")  # Redirect to a success page

    # Handle the case where the email verification object does not exist
    except ObjectDoesNotExist:
        # Invalid token
        return redirect("activation_failure")  # Redirect to a page indicating failure

    return redirect("login")


# resend_activation_email function to resend the activation email to the user
def resend_activation_email(request, user_id):
    try:
        # Retrieve the user object and email verification object based on the user ID provided in the URL parameters
        user = User.objects.get(id=user_id)
        email_verification = EmailVerification.objects.create(user=user)

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

        return redirect("confirmation_sent")

    except ObjectDoesNotExist:
        return redirect("activation_failure")  # Redirect to a page indicating failure

    return redirect("login")


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


# Activation_failure function view
def activation_failure(request, user_id):
    context = {"user_id": user_id}
    return render(request, "activation_failure.html", context)


# Logout function view
def logout_view(request):
    return render(request, "logout.html")


# Dashboard function view
def dashboard(request):
    chart_data = {"labels": [], "data": []}
    legendary_counts_data = {
        "labels": [],
        "data": [],
    }
    generations_counts_data = {
        "labels": [],
        "data": [],
    }
    # Initialize with labels and data keys
    if request.method == "POST":
        form = CsvFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                old_file = UploadCsvFile.objects.get(id=1)
                old_file.file.delete()
                csv_file_path = os.path.join(
                    settings.MEDIA_ROOT, "csv_files", "Pokemon.csv"
                )
                if os.path.exists(csv_file_path):
                    os.remove(csv_file_path)
            except UploadCsvFile.DoesNotExist:
                pass

            new_file = UploadCsvFile(file=request.FILES["file"])
            new_file.save()

            # Read the CSV file
            df = pd.read_csv(new_file.file.path)

            # Calculate missing values
            missing_values = df.isnull().sum()
            chart_data["labels"] = missing_values.index.tolist()
            chart_data["data"] = missing_values.values.tolist()

            # Calculate the counts of legendary Pokemon
            legendary_counts = df["Legendary"].value_counts().to_dict()
            legendary_counts_data["labels"] = list(legendary_counts.keys())
            legendary_counts_data["data"] = list(legendary_counts.values())

            # Calculate the counts of Generations
            generations_counts = df["Generation"].value_counts().to_dict()
            generations_counts_data["labels"] = list(generations_counts.keys())
            generations_counts_data["data"] = list(generations_counts.values())

            # Convert data to JSON
            chart_data_json = json.dumps(chart_data)
            legendary_counts_json = json.dumps(legendary_counts_data)
            generations_counts_json = json.dumps(generations_counts_data)

            df_html = df.head(20).to_html(
                classes="table table-dark table-hover", index=False
            )

            return render(
                request,
                "dashboard.html",
                {
                    "form": form,
                    "chart_data": chart_data_json,
                    "legendary_counts": legendary_counts_json,
                    "generations_counts": generations_counts_json,
                    "df_html": df_html,
                },
            )
    else:
        form = CsvFileForm()
    return render(request, "dashboard.html", {"form": form})


# Confirmation_sent function view
def confirmation_sent(request):
    return render(request, "confirmation_sent.html")


# Activation_success function view
def activation_success(request):
    return render(request, "activation_success.html")


# Activation_failure function view
def activation_failure(request):
    return render(request, "activation_failure.html")


def profile(request):
    # retrive the username of the logged in user
    user_name = User.objects.get(id=request.user.id).username
    user_email = User.objects.get(id=request.user.id).email
    return render(request, "profile.html")


def settings_profile(request):
    password_form = ChangePassword(user=request.user)
    email_form = ChangeEmail(user=request.user)

    if request.method == "POST":
        if "change_password" in request.POST:
            password_form = ChangePassword(request.POST, user=request.user)
            if password_form.is_valid():
                # replace the old password with the new password
                request.user.set_password(password_form.cleaned_data["new_password"])
                request.user.save()
                messages.success(request, "Your password has been changed")
                return redirect("settings_profile")
        elif "change_email" in request.POST:
            email_form = ChangeEmail(request.POST, user=request.user)
            if email_form.is_valid():
                request.user.email = email_form.cleaned_data["new_email"]
                request.user.save()
                messages.success(request, "Your email has been changed")
                return redirect("settings_profile")

    else:
        form = ChangeEmail(user=request.user)

    return render(
        request,
        "settings_profile.html",
        {"password_form": password_form, "email_form": email_form},
    )


def forgot_password(request):
    if request.method == "POST":
        form = RecoverPassword(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            new_password = form.cleaned_data.get("new_password")
            try:
                user = User.objects.get(username=username)
                user.password = make_password(new_password)
                user.save()
                return redirect("login")
            except User.DoesNotExist:
                form.add_error("username", "User does not exist")
    else:
        form = RecoverPassword()
    return render(request, "forgot_password.html", {"form": form})
