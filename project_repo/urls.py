from django.urls import path
from django.shortcuts import redirect
from . import views
from .views import (
    register, 
    teacher_register, 
    login_view, 
    forgot_password,  # Fixed import
    reset_password_view, 
    choose_role, 
    verify_email,
    verify_code,
    student_dashboard
)

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', login_view, name='login'),
    path('idea_form/', views.idea_form, name='idea_form'),
    path("student_dashboard/", student_dashboard, name="student_dashboard"),
    path('student_register/', register, name='register'),
    path('teacher-register/', teacher_register, name='teacher_register'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-code/", views.verify_code, name="verify_code"),
    path("verify-email/", verify_email, name="verify_email"),
    path("reset-password/<uidb64>/<token>/", reset_password_view, name="reset_password"),
    path('choose-role/', choose_role, name='choose_role'),
    path('reset/<uidb64>/<token>/', reset_password_view, name='password_reset_confirm'),
]
