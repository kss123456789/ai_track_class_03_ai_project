from django.db import models
from django.forms import DateTimeField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    # 일반 user 생성
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("must have user email")
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 관리자 user 생성
    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = None
    email = models.EmailField(
        default="", verbose_name="email", max_length=100, unique=True
    )

    # User 모델의 필수 field
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # 헬퍼 클래스 사용
    objects = UserManager()

    # 사용자의 username field는 email으로 설정
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class VideoData(models.Model):
    url = models.URLField(max_length=200)
    title = models.CharField(max_length=200)
    subtitles = models.TextField()
    summarized_subtitles = models.CharField(max_length=1000)
    translated_subtitles = models.CharField(max_length=1000)

    def __str__(self):
        return self.title


class PlayList(models.Model):
    list_name = models.CharField(max_length=50)
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="playlist_user",
        db_column="user_id",
        verbose_name="유저 ID",
    )
    video_data_id = models.ForeignKey(
        VideoData,
        on_delete=models.CASCADE,
        related_name='playlist_video_data',
        verbose_name='유튜브 동영상 데이터',
    )
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __str__(self):
        return f"User:{self.user_id} => PlayList:{self.list_name}"


class SearchLog(models.Model):
    user_id = models.ForeignKey(
        User, 
        related_name='searchlog',
        on_delete=models.CASCADE
    )
    video_data_id = models.ForeignKey(
        VideoData, 
        related_name='searchlog', 
        db_column="video_id", 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.id


class Rating(models.Model):
    user_id = models.ForeignKey(
        User, 
        related_name='rating',
        on_delete=models.CASCADE
    )
    video_data_id = models.ForeignKey(
        VideoData, 
        related_name='rating', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()

    def __int__(self):
        return self.id