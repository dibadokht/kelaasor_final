from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.api_urls")), 
    path("api/", include("courses.api_urls")), 
]
