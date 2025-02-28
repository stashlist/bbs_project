from django.urls import path
from .api_views import api_login, ThreadListCreateView, create_post, like_post

urlpatterns = [
    path("login/", api_login, name="api_login"),
    path("threads/", ThreadListCreateView.as_view(), name="thread_list_create"),  # ✅ スレッド作成エンドポイント
    path("posts/", create_post, name="api_create_post"),
    path("posts/<int:post_id>/like/", like_post, name="api_like_post"),
]
