from django.contrib.auth.hashers import make_password
from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=254)
    password = models.CharField(max_length=128)  # Ensure password hashing
    mobile = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10)
    branch = models.CharField(max_length=100)
    teacher_id = models.CharField(unique=True, max_length=50)
    institute = models.CharField(max_length=255)
    id_card = models.ImageField(upload_to='id_cards/', null=True, blank=True)

    # Fields for password reset
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):  # Avoid re-hashing already hashed passwords
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Student(models.Model):
    student_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    branch = models.CharField(max_length=100)
    institute = models.CharField(max_length=100)
    password = models.CharField(max_length=128)

    # Fields for password reset
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):  # Avoid re-hashing already hashed passwords
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
