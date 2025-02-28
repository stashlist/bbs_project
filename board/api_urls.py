from django.urls import path
from .api_views import api_login, create_thread, create_post, like_post

urlpatterns = [
    path("login/", api_login, name="api_login"),  # ✅ API エンドポイント
    path("threads/", create_thread, name="create_thread"),
    path("posts/", create_post, name="create_post"),
    path("posts/<int:post_id>/like/", like_post, name="like_post"),
]
