from django.contrib import admin
from .models import User
from .models import OTPCode

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("mobile", "first_name", "last_name", "role", "is_active", "is_staff", "created_at")
    search_fields = ("mobile", "first_name", "last_name", "email")
    list_filter = ("role", "is_active", "is_staff")
    ordering = ("-created_at",)
    fields = ("mobile", "first_name", "last_name", "email", "role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    
@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("mobile", "code", "is_used", "expires_at", "created_at", "attempts")
    list_filter = ("is_used",)
    search_fields = ("mobile", "code")

