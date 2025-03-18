from django.urls import path
from .views import register, teacher_register
from .views import login_view, teacher_register, verify_email, forgot_password_view, reset_password_view, choose_role
from .views import register, teacher_register, choose_role 
urlpatterns = [
    path('login/', login_view, name='login'),
    path('student_register/', register, name='register'),
  # Make sure this matches the name used in the template
    path('teacher-register/', teacher_register, name='teacher_register'),
    
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    # Use only one reset password URL that expects both user_type and token:
    path('reset-password/<str:user_type>/<str:token>/', reset_password_view, name='reset_password'),
    path('choose-role/', choose_role, name='choose_role'),
    path('teacher-registration/', teacher_register, name='teacher_register'),
    path('verify-email/', verify_email, name='verify_email'),
]
