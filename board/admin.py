from django.contrib import admin
from .models import Thread, Post, CustomUser  # ← ここを確認

admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(CustomUser)
