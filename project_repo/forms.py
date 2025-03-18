from django import forms
from .models import Teacher, Student
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Please Enter Team Lead Email / Founder'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Please Enter Your Password'}))
    captcha = CaptchaField()  # This adds the CAPTCHA field

class TeacherRegistrationForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['institute', 'name', 'email', 'mobile', 'gender', 'branch', 'teacher_id', 'id_card','password']

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'email', 'mobile', 'gender', 'branch', 'institute', 'password']