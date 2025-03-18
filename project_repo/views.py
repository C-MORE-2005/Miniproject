from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password  # Import password hashing
from .models import Teacher, Student
from .forms import LoginForm, TeacherRegistrationForm, StudentRegistrationForm


# Login View
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():  # This automatically validates the captcha
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid captcha. Please try again.")
    
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})

# Choose Role View
def choose_role(request):
    return render(request, 'choose_role.html')


# Teacher Registration View
def teacher_register(request):
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save(commit=False)  # Save but don't commit yet
            teacher.password = make_password(form.cleaned_data['password'])  # Hash password
            teacher.save()  # Now save to DB
            
            messages.success(request, "Registration successful! Please log in.")  # Success message
            return redirect("/login/")  # ✅ Redirect to login page
        else:
            messages.error(request, "Registration failed. Please check the form.")  # Error message
    
    else:
        form = TeacherRegistrationForm()
    
    return render(request, "teacher_registration.html", {"form": form})



# Student Registration View
def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.password = make_password(form.cleaned_data['password'])  # ✅ Secure password
            student.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'registration.html', {'form': form})


# Verify Email View
def verify_email(request):
    return render(request, 'verify_email.html')


# Forgot Password View
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
            token = get_random_string(length=50)  # Generate token
            
            # Save token in user record
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
                
            # Create reset password URL
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{user_type}/{token}/"
            
            # Send reset email
            subject = 'Password Reset Request'
            message = f'''
Hello,

You have requested to reset your password. Click the link below:

{reset_url}

This link expires in 24 hours.

If you did not request this, please ignore it.

Regards,  
Your Application Team
'''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, "A password reset link has been sent to your email.")
            except Exception as e:
                messages.error(request, f"Failed to send email. Try again later. Error: {str(e)}")
            
            return redirect('forgot_password')
        else:
            messages.info(request, "If this email exists, a reset link will be sent.")
            return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')


# Reset Password View
def reset_password_view(request, user_type, token):
    now = timezone.now()

    if user_type == 'teacher':
        try:
            user = Teacher.objects.get(reset_token=token, reset_token_expires__gt=now)
        except Teacher.DoesNotExist:
            messages.error(request, "The reset link is invalid or expired.")
            return redirect('forgot_password')
    elif user_type == 'student':
        try:
            user = Student.objects.get(reset_token=token, reset_token_expires__gt=now)
        except Student.DoesNotExist:
            messages.error(request, "The reset link is invalid or expired.")
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

        messages.success(request, "Password reset successfully. Log in with your new password.")
        return redirect('login')

    return render(request, 'reset_password.html')
