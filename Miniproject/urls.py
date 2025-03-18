from django.contrib import admin
from django.urls import path, include  # ✅ Include 'include' for captcha

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project_repo.urls')),  # Your app's URLs
    path('captcha/', include('captcha.urls')),  # ✅ Ensure this line is present
]
