import openai
import requests
import random
import time
import os
from django.contrib.auth import authenticate

# ✅ OpenAI API キー設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Django のエンドポイント設定（変更する）
BASE_URL = "https://bbs-project.onrender.com"
LOGIN_URL = f"{BASE_URL}/api/login/"
POST_URL = f"{BASE_URL}/api/posts/"
THREAD_URL = f"{BASE_URL}/api/threads/"
LIKE_URL = f"{BASE_URL}/api/posts/{'{post_id}'}/like/"
REPLY_URL = f"{BASE_URL}/api/posts/{'{post_id}'}/reply/"

# ✅ 自動ログイン情報（Bot 用のユーザーを作る）
BOT_USERNAME = "bot_user"
BOT_PASSWORD = "password123"

# ✅ セッション維持
session = requests.Session()

def login():
    """Bot ログイン"""
    data = {"username": BOT_USERNAME, "password": BOT_PASSWORD}
    response = session.post(LOGIN_URL, data=data)
    return response.status_code == 200

def generate_text(prompt):
    """ChatGPT で投稿内容を生成"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

def post_thread():
    """新しいスレッドを立てる"""
    title = generate_text("面白い掲示板のスレッドタイトルを考えてください。")
    first_post = generate_text("スレッドの最初の投稿内容を考えてください。")

    data = {"title": title, "content": first_post}
    response = session.post(THREAD_URL, json=data)
    
    if response.status_code == 201:
        print(f"✅ スレッド作成成功: {title}")
        return response.json().get("id")
    else:
        print(f"❌ スレッド作成失敗: {response.text}")
        return None

def post_reply(thread_id):
    """ランダムな投稿をする"""
    content = generate_text("掲示板の投稿内容を考えてください。")
    data = {"content": content, "thread_id": thread_id}
    response = session.post(POST_URL, json=data)

    if response.status_code == 201:
        print(f"✅ 投稿成功: {content}")
    else:
        print(f"❌ 投稿失敗: {response.text}")

def like_post(post_id):
    """ランダムにいいね"""
    response = session.post(LIKE_URL.format(post_id=post_id))
    if response.status_code == 200:
        print(f"👍 いいね: {post_id}")
    else:
        print(f"❌ いいね失敗: {response.text}")

def run_bot():
    """Bot のメイン処理"""
    if not login():
        print("❌ ログイン失敗")
        return

    while True:
        action = random.choice(["post_thread", "post_reply", "like"])
        
        if action == "post_thread":
            thread_id = post_thread()
            if thread_id:
                time.sleep(random.randint(10, 30))
                post_reply(thread_id)

        elif action == "post_reply":
            thread_id = random.randint(1, 10)  # 適当に既存スレッドを選ぶ
            post_reply(thread_id)

        elif action == "like":
            post_id = random.randint(1, 50)  # 適当に既存のポストを選ぶ
            like_post(post_id)

        time.sleep(random.randint(60, 300))  # 次のアクションまでの時間をランダムに設定

if __name__ == "__main__":
    run_bot()
