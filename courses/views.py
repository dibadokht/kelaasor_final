from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAdminUser , IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Enrollment, Section, Lesson , Order, OrderItem , Cart , CartItem
from .serializers import (CourseSerializer, EnrollmentSerializer, SectionSerializer,
    LessonPublicSerializer, LessonDetailSerializer , OrderSerializer, OrderCreateSerializer,
    CartItemSerializer , AddToCartSerializer)
from .filters import CourseFilter
from .permissions import IsEnrolledOrPreview
from django.utils import timezone

class CourseListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer
    filterset_class = CourseFilter                  
    filter_backends = [                            
        filters.OrderingFilter,
    ]
    ordering_fields = ["created_at", "price", "title"]  
    ordering = ["-created_at"]                         

    def get_queryset(self):
        return Course.objects.filter(is_active=True).order_by("-created_at")

class CourseDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer
    queryset = Course.objects.filter(is_active=True)
    lookup_field = "id"

class CourseCreateView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

class CourseUpdateView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    lookup_field = "id"

class CourseDeleteView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    lookup_field = "id"


class MyEnrollmentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related("course")

class EnrollmentCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        

class CourseSectionsView(ListAPIView):
   
    permission_classes = [AllowAny]
    serializer_class = SectionSerializer

    def get_queryset(self):
        course_id = self.kwargs["id"]
        return Section.objects.filter(course_id=course_id).prefetch_related("lessons")
    

class CourseLessonsListView(ListAPIView):
    permission_classes = [AllowAny]

    def _has_active_access(self, user, course_id):
        """
        Returns True if user is enrolled and (for offline courses) access is not expired.
        """
        if not (user and user.is_authenticated):
            return False

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return False

        # User must be enrolled and active
        enrolled = Enrollment.objects.filter(
            user=user,
            course_id=course_id,
            status="active"
        ).exists()
        if not enrolled:
            return False

        # For offline courses, enforce access end date
        today = timezone.now().date()
        if course.course_type == "offline" and course.end_date:
            if today > course.end_date:
                # Access expired
                return False

        return True

    def get_queryset(self):
        course_id = self.kwargs["id"]
        qs = Lesson.objects.filter(
            section__course_id=course_id
        ).select_related("section", "section__course")

        user = self.request.user
        has_access = self._has_active_access(user, course_id)

        # If user has active access → full lessons
        # Otherwise → only free preview lessons
        if has_access:
            return qs
        return qs.filter(is_free_preview=True)

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs["id"]
        queryset = self.get_queryset()

        # Use the same logic as get_queryset to decide serializer
        enrolled_with_access = self._has_active_access(request.user, course_id)

        from .serializers import LessonDetailSerializer, LessonPublicSerializer
        ser_class = LessonDetailSerializer if enrolled_with_access else LessonPublicSerializer
        serializer = ser_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from .models import Lesson


class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.select_related("section", "section__course")
    serializer_class = LessonDetailSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        return super().get_permissions()

    def get_object(self):
        obj = super().get_object()

        # Object-level permission: enrolled or preview
        from .permissions import IsEnrolledOrPreview
        perm = IsEnrolledOrPreview()
        if not perm.has_object_permission(self.request, self, obj):
            self.permission_denied(self.request, message=perm.message)

        #  Additional rule for offline courses: access expiry
        course = obj.section.course
        today = timezone.now().date()

        if course.course_type == "offline" and course.end_date:
            if today > course.end_date and not obj.is_free_preview:
                # Access to this offline content is expired
                raise PermissionDenied("Access to this offline course has expired.")

        return obj

    
#################################

 
class MyOrdersListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items", "items__course")

class OrderDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items", "items__course")

class OrderCreateView(CreateAPIView):
    """
    Create a pending order from list of course IDs.
    Body: { "course_ids": [1, 3, 5] }
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer
    def create(self, request, *args, **kwargs):
        user = request.user

        if not user.is_profile_complete():
            return Response(
                {
                    "detail": "please enter your name and firstname"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = ser.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderPayView(CreateAPIView):
   
    permission_classes = [IsAuthenticated]
    serializer_class = None  

    def post(self, request, *args, **kwargs):
        order_id = kwargs.get("id")
        try:
            order = Order.objects.select_related("user").prefetch_related("items", "items__course").get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status != "pending":
            return Response({"detail": f"Order already {order.status}."}, status=status.HTTP_400_BAD_REQUEST)


        order.status = "paid"
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "paid_at"])


        for item in order.items.all():
            Enrollment.objects.get_or_create(
                user=request.user,
                course=item.course,
                defaults={"status": "active"},
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

###########################################

class CartListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Each user has one cart; create it if it doesn't exist
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.select_related("course")
    
class AddToCartView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()  # returns CartItem

        output_data = CartItemSerializer(item).data
        return Response(output_data, status=status.HTTP_201_CREATED)
    
class RemoveFromCartView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Only allow deleting items from the current user's cart
        return CartItem.objects.filter(cart__user=self.request.user)
