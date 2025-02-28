from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("board.urls")),  # ← board のURLをルートに追加
    path("api/", include("board.api_urls")),
]
