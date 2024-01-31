from django.urls import path
from . import views

urlpatterns = [
    path("", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # Path for activating user account
    path("activate/<uuid:token>/", views.activate_account, name="activate_account"),
    # Path for resending activation email
    path(
        "resend-activation-email/<int:user_id>/",
        views.resend_activation_email,
        name="resend_activation_email",
    ),
    # Path for confirmation email sent page
    path("confirmation-sent/", views.confirmation_sent, name="confirmation_sent"),
    # Path for account activation success page
    path("activation-success/", views.activation_success, name="activation_success"),
    # Path for account activation failure page
    path("activation-failure/", views.activation_failure, name="activation_failure"),
    path("profile/", views.profile, name="profile"),
    path("settings_profile/", views.settings_profile, name="settings_profile"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
]
