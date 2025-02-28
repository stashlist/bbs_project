from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Thread, Post, Tag
import json
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView


@csrf_exempt
def api_login(request):
    """Bot も使えるログイン API"""
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"message": "ログイン成功"}, status=200)
        return JsonResponse({"error": "認証失敗"}, status=400)

    return JsonResponse({"error": "POST メソッドのみ対応"}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class ThreadListCreateView(CreateView):
    """スレッド作成・取得 API"""
    model = Thread
    fields = ["title"]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        title = data.get("title")
        first_post_content = data.get("first_post")
        tag_id = data.get("tag_id")

        if not title or not first_post_content:
            return JsonResponse({"error": "タイトルと内容は必須"}, status=400)

        # タグの処理
        tag = get_object_or_404(Tag, id=tag_id) if tag_id else Tag.objects.first()
        
        # スレッド作成
        thread = Thread.objects.create(title=title)
        if tag:
            thread.tags.add(tag)

        # 最初の投稿を作成
        Post.objects.create(thread=thread, user=request.user, content=first_post_content)

        return JsonResponse({"thread_id": thread.id, "title": thread.title}, status=201)


@csrf_exempt
@login_required
def create_post(request):
    """ポスト作成 API"""
    if request.method == "POST":
        data = json.loads(request.body)
        thread_id = data.get("thread_id")
        content = data.get("content")

        thread = Thread.objects.filter(id=thread_id).first()
        if not thread:
            return JsonResponse({"error": "スレッドが見つかりません"}, status=404)

        post = Post.objects.create(thread=thread, user=request.user, content=content)
        return JsonResponse({"message": "投稿成功", "id": post.id}, status=201)

    return JsonResponse({"error": "POST メソッドのみ対応"}, status=405)

@csrf_exempt
@login_required
def like_post(request, post_id):
    """投稿にいいね API"""
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return JsonResponse({"error": "投稿が見つかりません"}, status=404)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({"message": "いいね更新", "liked": liked, "total_likes": post.likes.count()}, status=200)
