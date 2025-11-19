
from django.db import models
from django.conf import settings

###############################
class Course(models.Model):
    COURSE_TYPES = [
        ("online", "Online"),   
        ("offline", "Offline"), 
    ]
    title = models.CharField(max_length=150)            
    course_type = models.CharField(max_length=7, choices=COURSE_TYPES, default="offline")
    price = models.PositiveIntegerField(default=0)      
    start_date = models.DateField(null=True, blank=True) 
    end_date = models.DateField(null=True, blank=True)   
    instructor_name = models.CharField(max_length=120, blank=True)  
    is_active = models.BooleanField(default=True)        
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.title

##################################

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")  
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} -> {self.course} ({self.status})"


##############################

class Section(models.Model):

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)  

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.course.title} :: {self.title}"
    
#################################

class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)
    content_url = models.URLField(blank=True)  
    is_free_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.section.title} :: {self.title}"


####################################

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    total_price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order #{self.pk} by {self.user} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey("courses.Course", on_delete=models.PROTECT, related_name="order_items")
    price_snapshot = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("order", "course")

    def __str__(self):
        return f"#{self.order_id} :: {self.course.title} ({self.price_snapshot})"
    
############################################

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.mobile}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "course") 

    def __str__(self):
        return f"{self.cart.user.mobile} -> {self.course.title}"

