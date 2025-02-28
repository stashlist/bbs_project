import requests
import random
import time
from django.views import View
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from board.models import Thread, Post, Tag

# API のエンドポイント
BASE_URL = "https://bbs-project.onrender.com/api/"

# Bot のログイン情報
BOT_USERNAME = "bot_user"
BOT_PASSWORD = "bot_password"

# Bot のセッション
session = requests.Session()

@method_decorator(csrf_exempt, name='dispatch')
class ThreadListCreateView(View):
    """スレッド作成・取得 API"""

    def get(self, request):
        """スレッド一覧を取得"""
        threads = Thread.objects.all().values("id", "title", "created_at")
        return JsonResponse(list(threads), safe=False)

    def post(self, request):
        """スレッドを作成"""
        data = json.loads(request.body)
        title = data.get("title")
        first_post_content = data.get("first_post")
        tag_id = data.get("tag_id")

        if not title or not first_post_content:
            return JsonResponse({"error": "タイトルと内容は必須"}, status=400)

        tag = Tag.objects.filter(id=tag_id).first() if tag_id else Tag.objects.first()

        thread = Thread.objects.create(title=title)
        if tag:
            thread.tags.add(tag)

        post = Post.objects.create(thread=thread, user=request.user, content=first_post_content)

        return JsonResponse({"id": thread.id, "title": thread.title}, status=201)

def login():
    """Bot をログインさせる"""
    response = session.post(f"{BASE_URL}login/", json={
        "username": BOT_USERNAME,
        "password": BOT_PASSWORD
    })
    if response.status_code == 200:
        print("✅ Bot ログイン成功")
    else:
        print("❌ ログイン失敗:", response.json())


def create_post(thread_id, content):
    """スレッドに投稿する"""
    payload = {"content": content}
    response = session.post(f"{BASE_URL}threads/{thread_id}/posts/", json=payload)

    if response.status_code == 201:
        post_id = response.json().get("id")
        print(f"✅ 投稿成功: ID={post_id}")
        return post_id
    else:
        print(f"❌ 投稿失敗: {response.status_code}, {response.json()}")
        return None



def create_thread(title, first_post, tag_id=None):
    """スレッドを作成する"""
    payload = {"title": title, "first_post": first_post}
    if tag_id:
        payload["tag_id"] = tag_id

    response = session.post(
        f"{BASE_URL}threads/", json=payload
    )

    if response.status_code == 201:
        thread_id = response.json().get("id")
        print(f"✅ スレッド作成成功: ID={thread_id}")
        return thread_id
    else:
        print(f"❌ スレッド作成失敗: {response.status_code}, {response.json()}")
        return None


def get_threads():
    """スレッド一覧を取得する"""
    try:
        response = session.get(f"{BASE_URL}threads/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ スレッド一覧取得失敗")
            return []
    except Exception as e:
        print(f"❌ スレッド一覧取得エラー: {e}")
        return []


def get_tags():
    """タグ一覧を取得する"""
    try:
        response = session.get(f"{BASE_URL}tags/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ タグ一覧取得失敗:")
            return []
    except Exception as e:
        print(f"❌ タグ一覧取得エラー: {e}")
        return []


def bot_action():
    """Bot のアクションループ（行動割合を調整）"""
    login()

    while True:
        action = random.choices(
            ["like_post", "create_post", "reply_post", "create_thread"],
            weights=[50, 30, 15, 5]
        )[0]

        if action == "create_thread":
            print("📝 新しいスレッドを作成します。")
            thread_title = "掲示板の自然なスレッドタイトル"
            first_post = "スレッドの最初の投稿内容"

            tag_list = get_tags()
            tag_id = random.choice(tag_list)["id"] if tag_list else None

            thread_id = create_thread(thread_title, first_post, tag_id)
            if thread_id:
                time.sleep(5)
                create_post(thread_id, first_post)

        elif action == "create_post":
            print("📝 既存のスレッドに投稿します。")
            existing_threads = get_threads()
            if existing_threads:
                thread_id = random.choice(existing_threads)["id"]
                post_content = "掲示板の自然な投稿"
                create_post(thread_id, post_content)
            else:
                print("⚠️ スレッドがないため、新規作成")
                thread_title = "新規スレッド"
                first_post = "スレッドの最初の投稿"
                tag_id = random.choice(get_tags())["id"] if get_tags() else None
                thread_id = create_thread(thread_title, first_post, tag_id)
                time.sleep(5)
                create_post(thread_id, first_post)

        # ⏳ **投稿の間隔をランダムに調整**
        sleep_time = random.randint(10, 60)
        print(f"⏳ 次のアクションまで {sleep_time} 秒待機")
        time.sleep(sleep_time)


if __name__ == "__main__":
    bot_action()
