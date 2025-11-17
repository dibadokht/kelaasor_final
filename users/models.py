from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import random
from datetime import timedelta
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError("Mobile is required")
        mobile = str(mobile).strip()
        user = self.model(mobile=mobile, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(mobile, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("student", "Student"), 
        ("support", "Support"),   
        ("admin", "Admin"),      
    ]

    mobile = models.CharField(max_length=15, unique=True)  
    first_name = models.CharField(max_length=50, blank=True)  
    last_name  = models.CharField(max_length=50, blank=True)  
    email = models.EmailField(blank=True)                   
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")  
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)   

    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)      

    objects = UserManager()

    USERNAME_FIELD = "mobile"    
    REQUIRED_FIELDS = []        

    def __str__(self):
        return self.mobile
    

def generate_otp_code(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))

class OTPCode(models.Model):
    mobile = models.CharField(max_length=15, db_index=True)
    code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_fresh(cls, mobile, ttl_seconds=120):
        now = timezone.now()
        return cls.objects.create(
            mobile=str(mobile).strip(),
            code=generate_otp_code(),
            expires_at=now + timedelta(seconds=ttl_seconds),
        )

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.mobile} - {self.code} (used={self.is_used})"


