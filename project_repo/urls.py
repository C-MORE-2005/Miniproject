from django.urls import path
from django.shortcuts import redirect
from .views import reset_password_view
from .views import reset_password_confirm_view  
from .views import student_dashboard
from .views import forgot_password_view
from .views import (
    register, 
    teacher_register, 
    login_view, 
    forgot_password_view, 
    reset_password_view, 
    choose_role, 
    verify_email
)

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', login_view, name='login'),
    path("student_dashboard/", student_dashboard, name="student_dashboard"),
    path('student_register/', register, name='register'),
    path('teacher-register/', teacher_register, name='teacher_register'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path("reset_password/", reset_password_view, name="reset_password"),
    path('choose-role/', choose_role, name='choose_role'),
    path('verify-email/', verify_email, name='verify_email'),
    path('reset/<uidb64>/<token>/', reset_password_confirm_view, name='password_reset_confirm'),
]

