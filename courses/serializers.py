from rest_framework import serializers
from .models import Course, Enrollment , Section, Lesson, Order, OrderItem

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "title", "course_type", "price",
            "start_date", "end_date", "instructor_name",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        ctype = attrs.get("course_type", getattr(self.instance, "course_type", None))
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))

        if ctype == "online" and not start_date:
            raise serializers.ValidationError(
                "For an 'online' course, 'start_date' is required."
            )
        return attrs



class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_title", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        course = attrs.get("course")
        if self.instance is None and Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        return attrs


class LessonPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "is_free_preview"]

class LessonDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order", "content_url", "is_free_preview"]

class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "title", "order", "lessons"]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "title", "course_type", "price",
            "start_date", "end_date", "instructor_name",
            "is_active", "created_at",
        ]

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_title", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source="course.title")
    class Meta:
        model = OrderItem
        fields = ["id", "course", "course_title", "price_snapshot"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id", "status", "total_price", "created_at", "paid_at", "items"]

class OrderCreateSerializer(serializers.Serializer):
    course_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False
    )

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        ids = list(dict.fromkeys(attrs["course_ids"]))  

        qs = Course.objects.filter(id__in=ids, is_active=True)
        if qs.count() != len(ids):
            raise serializers.ValidationError("One or more courses are invalid or inactive.")

        already = Enrollment.objects.filter(user=user, course_id__in=ids, status="active").values_list("course_id", flat=True)
        if already:
            raise serializers.ValidationError(f"You are already enrolled in courses: {list(already)}")

        attrs["courses_qs"] = list(qs)
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        courses = validated_data["courses_qs"]
        total = sum(c.price for c in courses)

        order = Order.objects.create(user=user, total_price=total, status="pending")
        items = [OrderItem(order=order, course=c, price_snapshot=c.price) for c in courses]
        OrderItem.objects.bulk_create(items)
        return order
