from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import run_migrations

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),  # GETでもログアウトOK
    path("profile/", views.profile, name="profile"),
    path("create_thread/", views.create_thread, name="create_thread"),  # スレッド作成
    path("", views.thread_list, name="thread_list"),  # スレッド一覧（トップページ）
    path("thread/<int:thread_id>/", views.thread_detail, name="thread_detail"),  # スレッド詳細ページ
    path("thread/<int:thread_id>/post/", views.add_post, name="add_post"),  # 投稿（レス）機能
    path("thread/<int:thread_id>/delete/", views.delete_thread, name="delete_thread"),
    path("ignored_users/", views.ignored_users_list, name="ignored_users_list"),
    path("ignore/<int:user_id>/", views.ignore_user, name="ignore_user"),  # **追加**
    path("unignore/<int:user_id>/", views.unignore_user, name="unignore_user"),
    path("following/", views.following_list, name="following_list"),
    path("followers/", views.followers_list, name="followers_list"),
    path("profile/<int:user_id>/", views.user_profile, name="user_profile"),
    path("follow/<int:user_id>/", views.follow_user, name="follow_user"),
    path("unfollow/<int:user_id>/", views.unfollow_user, name="unfollow_user"),
    path("threads/", views.thread_list, name="thread_list"),
    path("my_threads/", views.my_threads, name="my_threads"),
    path("my_posts/", views.my_posts, name="my_posts"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),  # プロフィール編集ページ
    path("kept_threads/", views.kept_threads, name="kept_threads"),
    path("thread/<int:thread_id>/keep/", views.toggle_keep_thread, name="toggle_keep_thread"),
    path("thread/<int:thread_id>/reply/<int:post_id>/", views.add_reply, name="add_reply"),  # ✅ 追加
    path("run-migrations/", run_migrations),
    path("verify/<int:user_id>/", views.verify_email, name="verify_email"),
    path("code_auth/", views.code_auth, name="code_auth"),
    path("resend_verification_code/<int:user_id>/", views.resend_verification_code, name="resend_verification_code"),
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("api/", include("board.api_urls")),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)