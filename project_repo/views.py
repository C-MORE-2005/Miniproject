from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from .models import Teacher, Student
from .forms import LoginForm
from .forms import TeacherRegistrationForm, StudentRegistrationForm

# Your existing login_view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to authenticate as Teacher
            try:
                user = Teacher.objects.get(email=email)
                if user.password == password:  # You should use password hashing!
                    # Create a session
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'teacher'
                    return redirect('teacher_dashboard')
            except Teacher.DoesNotExist:
                pass
                
            # Try to authenticate as Student
            try:
                user = Student.objects.get(email=email)
                if user.password == password:  # You should use password hashing!
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'student'
                    return redirect('student_dashboard')
            except Student.DoesNotExist:
                pass
                
            # If we get here, authentication failed
            messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def choose_role(request):
    return render(request, 'choose_role.html')

def teacher_register(request):
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
    else:
        form = TeacherRegistrationForm()
    return render(request, "teacher_registration.html", {"form": form})

def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration.html', {'form': form})

def verify_email(request):
    return render(request, 'verify_email.html')


# New forgot password view
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if email exists in Teacher or Student model
        teacher = None
        student = None
        
        try:
            teacher = Teacher.objects.get(email=email)
        except Teacher.DoesNotExist:
            pass
            
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            pass
            
        if teacher or student:
            # Generate token for password reset
            token = get_random_string(length=50)
            
            # Save token to user record
            if teacher:
                teacher.reset_token = token
                teacher.reset_token_expires = timezone.now() + timezone.timedelta(hours=24)
                teacher.save()
                user_type = 'teacher'
            else:
                student.reset_token = token
                student.reset_token_expires = timezone.now() + timezone.timedelta(hours=24)
                student.save()
                user_type = 'student'
                
            # Create password reset URL
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{user_type}/{token}/"
            
            # Send email with reset link
            subject = 'Password Reset Request'
            message = f'''
Hello,

You have requested to reset your password. Please click on the link below to reset your password:

{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Regards,
Your Application Team
'''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, "A password reset link has been sent to your email address.")
            except Exception as e:
                messages.error(request, f"Failed to send email. Please try again later. Error: {str(e)}")
            
            return redirect('forgot_password')
        else:
            # Don't reveal that email doesn't exist for security reasons
            messages.info(request, "If this email exists in our system, a password reset link will be sent.")
            return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')

# New reset password view
from django.contrib.auth.hashers import make_password  # Don't forget to import make_password

def reset_password_view(request, user_type, token):
    now = timezone.now()

    if user_type == 'teacher':
        try:
            user = Teacher.objects.get(reset_token=token, reset_token_expires__gt=now)
        except Teacher.DoesNotExist:
            messages.error(request, "The password reset link is invalid or has expired.")
            return redirect('forgot_password')
    elif user_type == 'student':
        try:
            user = Student.objects.get(reset_token=token, reset_token_expires__gt=now)
        except Student.DoesNotExist:
            messages.error(request, "The password reset link is invalid or has expired.")
            return redirect('forgot_password')
    else:
        messages.error(request, "Invalid user type.")
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'reset_password.html')

        # Securely store the password
        user.password = make_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.save()

        messages.success(request, "Your password has been reset successfully. You can now log in with your new password.")
        return redirect('login')

    return render(request, 'reset_password.html')
