from django.http import HttpResponse
from django.shortcuts import render, redirect
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
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

            # Check if CAPTCHA is correct
            if entered_captcha != session_captcha:
                messages.error(request, "Wrong CAPTCHA. Please try again.")
                return render(request, 'login.html', {'form': form})

            # Check if user exists in Teacher table
            teacher = Teacher.objects.filter(email=email).first()
            if teacher and check_password(password, teacher.password):
                request.session['user_id'] = teacher.id
                request.session['user_type'] = 'teacher'
                return redirect('teacher_dashboard')

            # Check if user exists in Student table
            student = Student.objects.filter(email=email).first()
            if student and check_password(password, student.password):
                request.session['user_id'] = student.id
                request.session['user_type'] = 'student'
                return redirect('student_dashboard')

            messages.error(request, "Invalid email or password. Please try again.")
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
            teacher.password = make_password(form.cleaned_data['password'])  # 🔹 Encrypt Password
            teacher.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("login")
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
            student.password = make_password(form.cleaned_data['password'])  # 🔹 Encrypt Password
            student.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'registration.html', {'form': form})


# Forgot Password View
def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Check if email exists in Student or Teacher table
        student = Student.objects.filter(email=email).first()
        teacher = Teacher.objects.filter(email=email).first()

        if student or teacher:
            verification_code = str(random.randint(100000, 999999))  # Generate 6-digit code
            verification_codes[email] = verification_code  # Store code with email

            # Send email
            send_mail(
                "Your Verification Code",
                f"Your verification code is {verification_code}",
                "patil.heena19@gmail.com",  # Replace with your email
                [email],
                fail_silently=False,
            )

            messages.success(request, "Verification code sent! Please enter the code below.")
            return redirect("verify_code")

        else:
            messages.error(request, "Email not found!")

    return render(request, "forgot_password.html")


# Reset Password Confirmation Vie
User = get_user_model()
def reset_password_view(request, uidb64, token):
    print("Reset Password View Called")  # Debugging

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        print("Decoded UID:", uid)  # Debugging

        # Try to find the user in the Student table first
        user = None
        if Student.objects.filter(student_id=uid).exists():
            user = Student.objects.get(student_id=uid)
            print("User Found in Student:", user.username)  # Debugging
        elif Teacher.objects.filter(teacher_id=uid).exists():
            user = Teacher.objects.get(student_id=uid)
            print("User Found in Teacher:", user.username)  # Debugging
        else:
            raise ValueError("User not found in Student or Teacher")

    except (TypeError, ValueError, OverflowError, Student.DoesNotExist, Teacher.DoesNotExist):
        messages.error(request, "Invalid or expired reset link.")
        return redirect('forgot_password')

    # Check if the reset token is valid
    if not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired reset token.")
        return redirect('forgot_password')

    # If the form is submitted
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        print("New Password Entered:", new_password)  # Debugging

        if not new_password or len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})

        user.set_password(new_password)  # Set and hash the new password
        user.save()
        print("Password Updated for:", user.username)  # Debugging

        messages.success(request, "Your password has been reset successfully! Please log in.")
        return redirect('login')

    return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})


# Verify Code View
def verify_code(request):
    if request.method == "POST":
        entered_code = request.POST["verification_code"]
        email = request.session.get("reset_email")  # Get email from session

        if email and verification_codes.get(email) == entered_code:
            request.session["verified_email"] = email  # Mark email as verified
            messages.success(request, "Code verified! Please reset your password.")
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid verification code.")
            return redirect("verify_code")

    return render(request, "verify_code.html")


# Student Dashboard
def student_dashboard(request):
    return render(request, 'student_dashboard.html')


# Teacher Dashboard
def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')


# Idea Form View
def idea_form(request):
    return render(request, "idea_form.html")


# Verify Email View
def verify_email(request):
    return HttpResponse("Email verification page")
