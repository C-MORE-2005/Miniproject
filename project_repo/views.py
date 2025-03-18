from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
import random
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password  # Import password hashing
from .models import Teacher, Student
from .forms import LoginForm, TeacherRegistrationForm, StudentRegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator



# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to authenticate as Teacher
            try:
                user = Teacher.objects.get(email=email)
                if user.password == password:  # ❌ Replace this with password hashing later!
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'teacher'
                    return redirect('teacher_dashboard')
            except Teacher.DoesNotExist:
                pass
                
            # Try to authenticate as Student
            try:
                user = Student.objects.get(email=email)
                if user.password == password:  # ❌ Replace this with password hashing later!
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'student'
                    return redirect('student_dashboard')
            except Student.DoesNotExist:
                pass
                
            messages.error(request, 'Invalid email or password')
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




# Forgot Password View
def reset_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")  # Get the email from form input

        # Check if the user exists
        try:
            user = User.objects.get(email=email)
            password = user.password  # Assuming passwords are stored in plain text (NOT RECOMMENDED)

            # Send email with the password
            send_mail(
                "Password Reset Request",
                f"Your password is: {password}",
                "your-email@gmail.com",  # From email
                [email],  # To email
                fail_silently=False,
            )

            messages.success(request, "Your password has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "This email is not registered.")

    return render(request, "reset_password.html")

# Reset Password View
def reset_password_view(request):
    email = request.GET.get("email")
    code = request.GET.get("code")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        user = User.objects.filter(email=email).first()

        if user and request.session.get("reset_code") == int(code):
            user.set_password(new_password)
            user.save()

            messages.success(request, "Password reset successfully!")
            return redirect("login")

    return render(request, "reset_password.html")





def verify_email(request):
    if request.method == "POST":
        email = request.session.get("email")
        entered_code = request.POST.get("verification_code")
        if verification_codes.get(email) == entered_code:
            messages.success(request, "Email verified! You can reset your password.")
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid verification code!")
    
    return redirect("forgot_password")





def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            # Generate password reset link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

            # Send email
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n{reset_link}',
                'your_email@gmail.com',  # Replace with your Gmail
                [email],
                fail_silently=False,
            )
            return render(request, 'forgot_password.html', {'message': 'Password reset link sent to your email!'})

        else:
            return render(request, 'forgot_password.html', {'error': 'Email not found'})

    return render(request, 'forgot_password.html')


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
            return redirect('login')  # Redirect to login page

        return render(request, 'reset_password.html')

    messages.error(request, "Invalid or expired reset link.")
    return redirect('forgot_password')  # Redirect back to forgot password page