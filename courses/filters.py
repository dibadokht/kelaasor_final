import django_filters
from .models import Course

class CourseFilter(django_filters.FilterSet):
    course_type = django_filters.CharFilter(field_name="course_type", lookup_expr="iexact")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Course
        fields = ["course_type", "min_price", "max_price"]
