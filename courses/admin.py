from django.contrib import admin
from .models import Course , Enrollment, Section, Lesson, Order, OrderItem

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "course_type", "price", "is_active", "created_at")
    list_filter = ("course_type", "is_active")
    search_fields = ("title", "instructor_name")
    ordering = ("-created_at",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "created_at")
    list_filter = ("status", "course")
    search_fields = ("user__mobile", "course__title")
    ordering = ("-created_at",)
    
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("course", "title", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("section", "title", "order", "is_free_preview")
    list_filter = ("section__course", "is_free_preview")
    search_fields = ("title", "section__title", "section__course__title")
    ordering = ("section", "order")
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("course", "price_snapshot")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at", "paid_at")
    list_filter = ("status",)
    search_fields = ("user__mobile",)
    ordering = ("-created_at",)
    inlines = [OrderItemInline]