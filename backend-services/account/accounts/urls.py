from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("setup-otp/", views.SetupOTPView.as_view(), name="setup_otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
