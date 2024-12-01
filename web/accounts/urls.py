from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("api/login/", views.CustomLoginView.as_view(), name="api_login"),
    path("api/logout/", views.LogoutView.as_view(), name="logout"),
    path("api/signup/", views.SignUpView.as_view(), name="signup"),
    path("api/setup-otp/", views.SetupOTPView.as_view(), name="setup_otp"),
    path("api/verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
]
