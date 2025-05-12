from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


# UserManager를 통해 사용자 생성 로직 정의
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)  # 비밀번호 암호화
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


# 커스터마이징된 User 모델
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"  # email을 username 필드로 설정
    REQUIRED_FIELDS = ["username"]  # 필수로 요구되는 필드

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin


class RefreshTokenLog(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
