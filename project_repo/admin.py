from django.contrib import admin
from .models import Student, Teacher

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'mobile', 'gender', 'branch', 'institute')
    search_fields = ('name', 'email', 'student_id', 'institute')
    list_filter = ('branch', 'gender', 'institute')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'branch', 'teacher_id', 'institute')
    search_fields = ('name', 'email', 'teacher_id')
    list_filter = ('branch', 'gender', 'institute')
