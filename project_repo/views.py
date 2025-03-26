from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from captcha.models import CaptchaStore
from django.contrib.auth import authenticate, login
from captcha.helpers import captcha_image_url
from .models import Teacher, Student
from .forms import LoginForm, TeacherRegistrationForm, StudentRegistrationForm

# Temporary dictionary to store email verification codes
verification_codes = {}

# Login View
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Received Email: {email}, Password: {password}")  # Debugging

        # Skip captcha validation (TEMPORARY)
        user = None
        user_type = None

        student = Student.objects.filter(email=email).first()
        if student and check_password(password, student.password):
            user = student
            user_type = "student"

        teacher = Teacher.objects.filter(email=email).first()
        if teacher and check_password(password, teacher.password):
            user = teacher
            user_type = "teacher"

        if user:
            request.session["user_type"] = user_type
            request.session["user_id"] = user.id
            print(f"Redirecting to {user_type}_dashboard")  # Debugging
            return redirect("student_dashboard" if user_type == "student" else "teacher_dashboard")

        messages.error(request, "Invalid email or password.")
    
    return render(request, "login.html")


# Choose Role View
def choose_role(request):
    return render(request, 'choose_role.html')

# Teacher Registration View
def teacher_register(request):
    form = TeacherRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        teacher = form.save(commit=False)
        teacher.password = make_password(form.cleaned_data['password'])
        teacher.save()
        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")
    
    return render(request, "teacher_registration.html", {"form": form})

# Student Registration View
def register(request):
    form = StudentRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.password = make_password(form.cleaned_data['password'])
        student.save()
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'registration.html', {'form': form})

# Forgot Password View
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = Student.objects.filter(email=email).first() or Teacher.objects.filter(email=email).first()
        if user:
            verification_code = str(random.randint(100000, 999999))
            request.session["verification_code"] = verification_code  # Store in session
            request.session["reset_email"] = email  # Store email in session
            send_mail("Your Verification Code", f"Your verification code is {verification_code}", "patil.heena19@gmail.com", [email])
            messages.success(request, "Verification code sent! Please enter the code below.")
            return redirect("verify_code")
        messages.error(request, "Email not found!")
    
    return render(request, "forgot_password.html")

# Reset Password Confirmation View
User = get_user_model()
def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        student = Student.objects.filter(id=uid).first()
        teacher = Teacher.objects.filter(id=uid).first()
        user = student if student else teacher

        if not user or not default_token_generator.check_token(user, token):
            messages.error(request, "Invalid or expired reset link.")
            return redirect('forgot_password')

    except Exception:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        else:
            user.password = make_password(new_password)  # Hash new password
            user.save()
            request.session.flush()  # Clear session for security
            messages.success(request, "Your password has been reset successfully! Please log in.")
            return redirect('login')
    
    return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})

# Verify Code View
def verify_code(request):
    if request.method == "POST":
        entered_code = request.POST.get("verification_code")
        email = request.session.get("reset_email")
        stored_code = request.session.get("verification_code")

        if email and stored_code and entered_code == stored_code:
            request.session["verified_email"] = email
            del request.session["verification_code"]  # Remove used code
            messages.success(request, "Code verified! Please reset your password.")
            return redirect("reset_password")
        messages.error(request, "Invalid verification code.")
    
    return render(request, "verify_code.html")

# Student Dashboard
def student_dashboard(request):
    if request.session.get("user_type") != "student":
        return redirect("login")
    return render(request, 'student_dashboard.html')

# Teacher Dashboard
def teacher_dashboard(request):
    if request.session.get("user_type") != "teacher":
        return redirect("login")
    return render(request, 'teacher_dashboard.html')

# Idea Form View
def idea_form(request):
    return render(request, "idea_form.html")

def prototype_form(request):
    return render(request, "prototype_form.html")

def start_up(request):
    return render(request, "start_up.html")

# Verify Email View
def verify_email(request):
    return HttpResponse("Email verification page")

# Captcha Views
def refresh_captcha(request):
    """Generate and return a new captcha key and image URL."""
    new_captcha = CaptchaStore.generate_key()  # Generate new captcha
    new_captcha_url = captcha_image_url(new_captcha)  # Get new captcha image URL
    return JsonResponse({'captcha_key': new_captcha, 'captcha_url': new_captcha_url})

def captcha_image(request):
    text = generate_captcha_text()
    request.session["captcha"] = text

    img = Image.new("RGB", (150, 50), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")
