from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings # 追加
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
import random
import uuid
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from asgiref.sync import sync_to_async

def get_random_default_avatar():
    """media/default/ 内の .svg ファイルからランダムにデフォルト画像を選択"""
    default_path = os.path.join(settings.MEDIA_ROOT, "default")
    if os.path.exists(default_path):
        svg_files = [f for f in os.listdir(default_path) if f.endswith(".svg")]
        if svg_files:
            return f"default/{random.choice(svg_files)}"  # `media/default/` からランダム選択
    return "default/1f60a.svg"  # `.svg` がない場合のデフォルト

def avatar_upload_path(instance, filename):
    """アップロードされた画像のファイル名をランダムな一意の名前に変更"""
    ext = filename.split('.')[-1]  # ファイルの拡張子を取得
    new_filename = f"{uuid.uuid4().hex}.{ext}"  # ランダムなファイル名に変更
    return os.path.join("avatars/", new_filename)

class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, email, username, password=None):
        if not user_id or not email or not username:
            raise ValueError("ユーザーID・メールアドレス・ユーザーネームは必須です")
        email = self.normalize_email(email)

        user = self.model(
            user_id=user_id, email=email, username=username,
            default_avatar=get_random_default_avatar()  # ランダムな `.svg` を設定
        )
        user.set_password(password)
        user.save(using=self._db)
        return user



class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    default_avatar = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    kept_threads = models.ManyToManyField("Thread", related_name="kept_by", blank=True)

    # メール認証用のフィールド
    is_verified = models.BooleanField(default=False)  # 仮登録フラグ
    verification_code = models.CharField(max_length=5, blank=True, null=True)  # 5桁の認証コード

    objects = CustomUserManager()

    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["email", "username"]

    def get_profile_image(self):
        """ユーザーが `avatar` を設定していればそれを使い、なければ `default_avatar` を使用"""
        if self.avatar:
            return f"{settings.MEDIA_URL}{self.avatar}"
        if self.default_avatar:
            return f"{settings.MEDIA_URL}{self.default_avatar}"
        
        # 1〜25 のランダムな番号を選んでデフォルト画像として使用
        random_number = random.randint(1, 25)
        return f"{settings.MEDIA_URL}default/{random_number}.svg"


class Tag(models.Model):
    """タグモデル"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Thread(models.Model):
    title = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True)  # ✅ 複数のタグを設定可能にする
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # **修正**
    post_count = models.IntegerField(default=0)  # ✅ 新しく追加

class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    
    # 追加: いいね機能
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()
    
    async def total_likes_async(self):
        return await sync_to_async(self.likes.count)()

    
# ✅ 投稿が追加されたら `post_count` を +1
@receiver(post_save, sender=Post)
def update_post_count_on_create(sender, instance, created, **kwargs):
    if created:
        Thread.objects.filter(id=instance.thread_id).update(post_count=models.F("post_count") + 1)

# ✅ 投稿が削除されたら `post_count` を -1
@receiver(post_delete, sender=Post)
def update_post_count_on_delete(sender, instance, **kwargs):
    Thread.objects.filter(id=instance.thread_id).update(post_count=models.F("post_count") - 1)    




User = get_user_model()  # Django のユーザーモデルを取得



class IgnoredUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ignoring")
    ignored_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ignored_by")

    class Meta:
        unique_together = ('user', 'ignored_user')  # 同じユーザーを複数回無視しないようにする


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ('follower', 'followed')  # 同じユーザーを複数回フォローできないようにする


class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"
