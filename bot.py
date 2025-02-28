import requests
import random
import time

# API のエンドポイント
BASE_URL = "https://bbs-project.onrender.com/api/"

# Bot のログイン情報
BOT_USERNAME = "bot_user"
BOT_PASSWORD = "bot_password"

# Bot のアクション頻度設定
POST_INTERVAL = random.randint(30, 180)  # 30秒 〜 3分 の間でランダム投稿

# Bot のセッション
session = requests.Session()

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

def create_thread():
    """ランダムなスレッドを作成"""
    title = f"Bot のスレッド {random.randint(1, 1000)}"
    content = f"このスレッドは Bot が自動で作成しました！（{random.randint(1, 100)}）"

    response = session.post(f"{BASE_URL}threads/", json={
        "title": title,
        "content": content
    })

    if response.status_code == 201:
        thread_id = response.json()["id"]
        print(f"✅ スレッド作成成功: {title}（ID: {thread_id}）")
        return thread_id
    else:
        print("❌ スレッド作成失敗:", response.json())
        return None

def create_post(thread_id):
    """スレッドに投稿"""
    messages = [
        "これは自動投稿です。",
        "ボットがランダムに書き込みました！",
        "Django と WebSocket は便利ですね。",
        "みんなこのスレどう思う？",
        "質問ある人？",
    ]
    content = random.choice(messages)

    response = session.post(f"{BASE_URL}posts/", json={
        "thread_id": thread_id,
        "content": content
    })

    if response.status_code == 201:
        post_id = response.json()["id"]
        print(f"✅ 投稿成功: {content}（ID: {post_id}）")
        return post_id
    else:
        print("❌ 投稿失敗:", response.json())
        return None

def like_post(post_id):
    """投稿にいいねをつける"""
    response = session.post(f"{BASE_URL}posts/{post_id}/like/")
    if response.status_code == 200:
        print(f"👍 いいね！ 投稿 ID: {post_id}")
    else:
        print("❌ いいね失敗:", response.json())

def bot_action():
    """Bot のアクションループ"""
    login()
    
    while True:
        action = random.choice(["create_thread", "create_post", "like_post"])
        
        if action == "create_thread":
            thread_id = create_thread()
            if thread_id:
                time.sleep(5)  # スレッド作成後少し待つ
                create_post(thread_id)

        elif action == "create_post":
            existing_threads = session.get(f"{BASE_URL}threads/").json()
            if existing_threads:
                thread_id = random.choice(existing_threads)["id"]
                create_post(thread_id)

        elif action == "like_post":
            existing_posts = session.get(f"{BASE_URL}posts/").json()
            if existing_posts:
                post_id = random.choice(existing_posts)["id"]
                like_post(post_id)

        time.sleep(POST_INTERVAL)

if __name__ == "__main__":
    bot_action()
