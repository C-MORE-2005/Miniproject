from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth import views as auth_views # ✅ Include 'include' for captcha

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project_repo.urls')),  # Your app's URLs
    path('captcha/', include('captcha.urls')),  # ✅ Ensure this line is present
     path("reset_password/", auth_views.PasswordResetView.as_view(template_name="reset_password.html"), name="reset_password"),
    # Password reset email sent confirmation
    path("reset_password_sent/", auth_views.PasswordResetDoneView.as_view(template_name="reset_password_sent.html"), name="password_reset_done"),
    # Password reset link confirmation (via email)
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="reset_password_confirm.html"), name="password_reset_confirm"),
    # Password successfully changed confirmation
    path("reset_password_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="reset_password_complete.html"), name="password_reset_complete"),
]
