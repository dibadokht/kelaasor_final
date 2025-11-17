from rest_framework.permissions import BasePermission
from .models import Enrollment, Course

class IsEnrolledOrPreview(BasePermission):
    """
    Allow access if:
    - lesson is marked as free preview, OR
    - request.user is enrolled in the course
    """
    message = "You must be enrolled in this course to access this content."

    def has_object_permission(self, request, view, obj):
        # obj can be a Lesson; get its course via section.course
        course = obj.section.course
        if obj.is_free_preview:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(user=request.user, course=course, status="active").exists()
