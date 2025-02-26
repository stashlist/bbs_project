from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import ThreadForm, PostForm, ProfileForm
from .models import Thread, Post, Follow, User
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import IgnoredUsers, User
from django.db.models import Case, When, Value, BooleanField
import json


# ユーザー登録（サインアップ）
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("thread_list")
        else:
            # フォームエラーをコンソールに出力（デバッグ用）
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, "board/signup.html", {"form": form})

# プロフィールページ（ログイン必須）
@login_required
def profile(request):
    following_count = Follow.objects.filter(follower=request.user).count()
    followers_count = Follow.objects.filter(followed=request.user).count()
    threads_count = Thread.objects.filter(creator=request.user).count()
    posts_count = Post.objects.filter(user=request.user).count()

    return render(request, "board/profile.html", {
        "following_count": following_count,
        "followers_count": followers_count,
        "threads_count": threads_count,
        "posts_count": posts_count,
    })



# スレッド作成ページ
@login_required(login_url='/login/')
def create_thread(request):
    if request.method == "POST":
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)  # フォームのデータを一時保存（まだDBには保存しない）
            thread.creator = request.user  # **ログインしているユーザーを作成者に設定**
            thread.save()  # **DBに保存**
            form.cleaned_data["tags"]  # タグを取得
            thread.tags.set(form.cleaned_data["tags"])  # タグをスレッドにセット
            
            
            # 最初の投稿を作成
            Post.objects.create(
                thread=thread,
                user=request.user,  # **ログインしているユーザーを投稿者に設定**
                content=form.cleaned_data["first_post_content"]
            )

            return redirect("thread_list")
    else:
        form = ThreadForm()
    
    return render(request, "board/create_thread.html", {"form": form})



def thread_list(request):
    threads = Thread.objects.all().order_by("-created_at")  # 新しいスレッド順

    # フィルタリング条件の取得
    title_query = request.GET.get("title", "")
    title_match = request.GET.get("title_match", "contains")  # デフォルトは部分一致
    tags_query = request.GET.get("tags", "")
    followed_filter = request.GET.get("followed_only", "off")  # フォローしているユーザーのスレッドのみ表示するか
    my_posts_filter = request.GET.get("my_posts_only", "off")  # 自分がレスを付けたスレッドのみ表示するか

    # タイトルのフィルタリング
    if title_query:
        if title_match == "contains":
            threads = threads.filter(title__icontains=title_query)
        elif title_match == "startswith":
            threads = threads.filter(title__startswith=title_query)
        elif title_match == "endswith":
            threads = threads.filter(title__endswith=title_query)

    # タグのフィルタリング
    if tags_query:
        threads = threads.filter(tags__icontains=tags_query)

    # フォローしているユーザーのスレッドのみ表示
    if request.user.is_authenticated and followed_filter == "on":
        followed_users = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)
        threads = threads.filter(creator_id__in=followed_users)

    # 自分がレスを付けたスレッドのみ表示
    if request.user.is_authenticated and my_posts_filter == "on":
        my_posted_threads = Post.objects.filter(user=request.user).values_list('thread', flat=True)
        threads = threads.filter(id__in=my_posted_threads)
    
    # **無視リストの適用**
    ignored_users = []
    if request.user.is_authenticated:
        ignored_users = IgnoredUsers.objects.filter(user=request.user).values_list('ignored_user', flat=True)
        
        # 無視リストにいる作成者のスレッドを非表示にする
        threads = threads.annotate(is_ignored=Case(
            When(creator_id__in=ignored_users, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))
    
    # タグをリスト化して渡す
    for thread in threads:
        thread.tag_list = thread.tags.all()

    return render(request, "board/thread_list.html", {"threads": threads, "ignored_users": ignored_users})


def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    
    # **post を取得し、関連する `parent_id` も一緒に取得**
    posts = Post.objects.filter(thread=thread).order_by("created_at").select_related("user", "parent_post")


    ignored_users = []
    if request.user.is_authenticated:
        ignored_users = list(IgnoredUsers.objects.filter(user=request.user).values_list('ignored_user', flat=True))

        # **無視リストにいるユーザーのレスを非表示にする**
        posts = posts.annotate(is_ignored=Case(
            When(user_id__in=ignored_users, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))

    # **スレッド内の連番を付与**
    post_index_map = {}  # {post.id: index} のマッピングを作成
    for index, post in enumerate(posts, start=1):
        post.thread_index = index
        post_index_map[post.id] = index  # IDとスレッド内の番号を関連付ける

    # **親ポストのレス番号を設定**
    for post in posts:
        if post.parent_post:
            post.parent_thread_index = post_index_map.get(post.parent_post.id, None)
    
    return render(request, "board/thread_detail.html", {
        "thread": thread,
        "posts": posts,
        "ignored_users": json.dumps(ignored_users),  # **JSON 形式で JavaScript に渡す**
    })



@login_required
def delete_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    # **スレッド作成者のみ削除を許可**
    if request.user != thread.creator:
        return HttpResponseForbidden("このスレッドを削除する権限がありません。")

    thread.delete()
    return redirect("thread_list")


@login_required
def add_post(request, thread_id):
    print("add_postメソッド")
    if request.method == "POST":
        print("🟢 add_post が呼ばれました")  # デバッグ用ログ
        thread = Thread.objects.get(id=thread_id)
        content = request.POST.get("content")

        if content:
            post = Post.objects.create(
                thread=thread,
                user=request.user,
                content=content
            )
            print(f"🟢 投稿を作成: ID={post.id}, 内容={post.content}")

        return redirect("thread_detail", thread_id=thread_id)

@login_required
def ignore_user(request, user_id):
    ignored_user = get_object_or_404(User, id=user_id)
    
    # すでに無視リストに入っていなければ追加
    if not IgnoredUsers.objects.filter(user=request.user, ignored_user=ignored_user).exists():
        IgnoredUsers.objects.create(user=request.user, ignored_user=ignored_user)
    
    return redirect(request.META.get('HTTP_REFERER', 'thread_list'))

@login_required
def ignored_users_list(request):
    ignored_users = IgnoredUsers.objects.filter(user=request.user)
    return render(request, "board/ignored_users.html", {"ignored_users": ignored_users})

@login_required
def unignore_user(request, user_id):
    User = get_user_model()  # Django のカスタムユーザーモデルを取得
    ignored_user = get_object_or_404(User, id=user_id)
    IgnoredUsers.objects.filter(user=request.user, ignored_user=ignored_user).delete()
    return redirect("ignored_users_list")


@login_required
def follow_user(request, user_id):
    followed_user = get_object_or_404(User, id=user_id)
    
    # すでにフォローしていない場合のみ追加
    if not Follow.objects.filter(follower=request.user, followed=followed_user).exists():
        Follow.objects.create(follower=request.user, followed=followed_user)
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def unfollow_user(request, user_id):
    followed_user = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, followed=followed_user).delete()
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

def following_list(request):
    following = Follow.objects.filter(follower=request.user)
    return render(request, "board/following_list.html", {"following": following})

def followers_list(request):
    followers = Follow.objects.filter(followed=request.user)
    return render(request, "board/followers_list.html", {"followers": followers})

def my_threads(request):
    threads = Thread.objects.filter(creator=request.user).order_by("-created_at")
    return render(request, "board/my_threads.html", {"threads": threads})

def my_posts(request):
    posts = Post.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "board/my_posts.html", {"posts": posts})

def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    # フォローしているか確認
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, followed=profile_user).exists()

    return render(request, "board/user_profile.html", {
        "profile_user": profile_user,
        "is_following": is_following
    })

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "board/profile_edit.html", {"form": form})

@login_required
def kept_threads(request):
    kept_threads = request.user.kept_threads.all()
    return render(request, "board/kept_threads.html", {"kept_threads": kept_threads})

@login_required
def toggle_keep_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if thread in request.user.kept_threads.all():
        request.user.kept_threads.remove(thread)
    else:
        request.user.kept_threads.add(thread)
    return redirect("thread_detail", thread_id=thread.id)


@login_required
def add_reply(request, thread_id, post_id):
    """リプライを追加する"""
    thread = get_object_or_404(Thread, id=thread_id)
    parent_post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("reply_content")
        if content:
            Post.objects.create(thread=thread, user=request.user, content=content, parent_post=parent_post)

    return redirect("thread_detail", thread_id=thread_id)