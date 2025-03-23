from django.urls import path
from django.shortcuts import redirect
from project_repo import views  # Import views from project_repo
from django.urls import path, include
from project_repo.views import prototype_form  # Ensure this line is present

from project_repo.views import (
    register, 
    teacher_register, 
    login_view, 
    forgot_password,  
    reset_password_view, 
    choose_role, 
    verify_email,
    verify_code,
    student_dashboard,
    teacher_dashboard,
    refresh_captcha, 
    captcha_image,
    idea_form,
    prototype_form,
    start_up
)

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', login_view, name='login'),
    path('idea_form/',idea_form, name='idea_form'),
    path('prototype_form/',prototype_form, name='prototype_form'),
    path('start_up/',start_up, name='start_up'),
    path("student_dashboard/", student_dashboard, name="student_dashboard"),
    path("teacher_dashboard/", teacher_dashboard, name="teacher_dashboard"),
    path('student_register/', register, name='register'),
    path('teacher-register/', teacher_register, name='teacher_register'),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("verify-code/", verify_code, name="verify_code"),
    path("verify-email/", verify_email, name="verify_email"),
    path("reset-password/<uidb64>/<token>/", reset_password_view, name="reset_password"),
    path('choose-role/', choose_role, name='choose_role'),
    path('reset/<uidb64>/<token>/', reset_password_view, name='password_reset_confirm'),
    path('refresh-captcha/', refresh_captcha, name='refresh_captcha'),
    path('captcha-image/', captcha_image, name='captcha_image'),
    path('captcha/', include('captcha.urls')),
]
