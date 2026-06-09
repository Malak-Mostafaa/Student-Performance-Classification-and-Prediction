from django.contrib import admin
from django.urls import path, include
from students import views as students_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('students.urls')),   # student dashboard routes
    path('instructor/', include('instructors.urls')),  # instructor dashboard routes
]