from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.urls import reverse
from .models import Teacher, Student
from .forms import LoginForm, TeacherRegistrationForm, StudentRegistrationForm

# Dictionary to store email verification codes
verification_codes = {}


# Login View

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            entered_captcha = request.POST.get("captcha")
            session_captcha = request.session.get("captcha_value")  # Get stored CAPTCHA

            # 1. Check if the CAPTCHA is correct
            if entered_captcha != session_captcha:
                messages.error(request, "Wrong CAPTCHA. Please enter again.")
                return render(request, 'login.html', {'form': form})

            # 2. Check if the user exists in Teacher table
            try:
                user = Teacher.objects.get(email=email)
                if check_password(password, user.password):  # Compare hashed passwords
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'teacher'
                    return redirect('teacher_dashboard')
                else:
                    messages.error(request, "Incorrect password.")
                    return render(request, 'login.html', {'form': form})

            except Teacher.DoesNotExist:
                pass  # Continue to check Student

            # 3. Check if the user exists in Student table
            try:
                user = Student.objects.get(email=email)
                if check_password(password, user.password):  # Compare hashed passwords
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'student'
                    return redirect('student_dashboard')
                else:
                    messages.error(request, "Incorrect password.")
                    return render(request, 'login.html', {'form': form})

            except Student.DoesNotExist:
                messages.error(request, "User not found. Please register first.")
                return render(request, 'login.html', {'form': form})

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Choose Role View
def choose_role(request):
    return render(request, 'choose_role.html')


# Teacher Registration View
def teacher_register(request):
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.password = make_password(form.cleaned_data['password'])  # ✅ Hash password
            teacher.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("/login/")
        else:
            messages.error(request, "Registration failed. Please check the form.")

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


# Forgot Password View
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            # Generate password reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(reverse('reset_password_confirm', kwargs={'uidb64': uid, 'token': token}))

            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n{reset_link}',
                'your_email@gmail.com',  # Replace with your email
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Password reset link sent to your email!')
            return redirect('login')
        else:
            messages.error(request, 'Email not found.')

    return render(request, 'forgot_password.html')


# Reset Password Confirmation View
User = get_user_model()

def reset_password_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')

            if len(new_password) < 6:  # Basic password validation
                messages.error(request, "Password must be at least 6 characters.")
                return render(request, 'reset_password.html')

            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been reset successfully! Please log in.")
            return redirect('login')

        return render(request, 'reset_password.html')

    messages.error(request, "Invalid or expired reset link.")
    return redirect('forgot_password')


# Verify Email View
def verify_email(request):
    if request.method == "POST":
        email = request.session.get("email")
        entered_code = request.POST.get("verification_code")
        
        if email in verification_codes and verification_codes[email] == entered_code:
            messages.success(request, "Email verified! You can reset your password.")
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid verification code!")
    
    return redirect("forgot_password")


def reset_password_view(request):
    return HttpResponse("Reset password page under construction.")

