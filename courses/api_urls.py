from django.urls import path
from .views import (
    CourseListView, CourseDetailView,
    CourseCreateView, CourseUpdateView, CourseDeleteView,
     MyEnrollmentListView, EnrollmentCreateView,
     CourseSectionsView, CourseLessonsListView, LessonDetailView,
     MyOrdersListView, OrderDetailView, OrderCreateView, OrderPayView,
)

urlpatterns = [
    # courses
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<int:id>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/create/", CourseCreateView.as_view(), name="course-create"),
    path("courses/<int:id>/update/", CourseUpdateView.as_view(), name="course-update"),
    path("courses/<int:id>/delete/", CourseDeleteView.as_view(), name="course-delete"),
    
    # enrollments
    path("enrollments/mine/", MyEnrollmentListView.as_view(), name="my-enrollments"),
    path("enrollments/create/", EnrollmentCreateView.as_view(), name="enrollment-create"),
    
    # content
    path("courses/<int:id>/sections/", CourseSectionsView.as_view(), name="course-sections"),
    path("courses/<int:id>/lessons/", CourseLessonsListView.as_view(), name="course-lessons"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    
    # orders
    path("orders/mine/", MyOrdersListView.as_view(), name="my-orders"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:id>/pay/", OrderPayView.as_view(), name="order-pay"),  # fake payment
]
