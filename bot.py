import requests
import random
import time
import openai

# API のエンドポイント
BASE_URL = "https://bbs-project.onrender.com/api/"

# Bot のログイン情報
BOT_USERNAME = "bot_user"
BOT_PASSWORD = "bot_password"


# OpenAIのクライアントを作成
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Bot のアクション頻度設定
POST_INTERVAL = random.randint(30, 180)

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

# API呼び出し関数
def generate_text(prompt):
    """Ollama を使ってテキストを生成（ストリームデータ対応）"""
    data = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False  # ストリームをオフにする
    }

    response = requests.post(OLLAMA_URL, json=data)

    try:
        # Ollama のレスポンスはストリーム（NDJSON）なので最初の行だけ取得
        response_json = response.json()
        return response_json.get("response", "").strip()
    
    except requests.exceptions.JSONDecodeError as e:
        print("❌ JSON デコードエラー:", e)
        print("レスポンス内容:", response.text)
        return "エラーが発生しました"

def bot_action():
    """Bot のアクションループ"""
    login()

    while True:
        action = random.choice(["create_thread", "create_post", "like_post"])

        if action == "create_thread":
            thread_title = generate_text("掲示板で自然に見えるスレッドタイトルを1つ考えてください。")
            first_post = generate_text("そのスレッドの最初の投稿を1つ考えてください。")

            thread_id = create_thread(thread_title, first_post)
            if thread_id:
                print(f"✅ スレッド作成: {thread_title}")
                time.sleep(random.randint(30, 300))
                create_post(thread_id)

        elif action == "create_post":
            response = session.get(f"{BASE_URL}threads/")
            existing_threads = response.json() if response.status_code == 200 else []

            if existing_threads:
                thread_id = random.choice(existing_threads)["id"]
                post_content = generate_text("掲示板で自然に見える返信を1つ考えてください。")
                create_post(thread_id, post_content)
            else:
                print("⚠️ スレッドがないため、新規投稿をスキップ")

        elif action == "like_post":
            response = session.get(f"{BASE_URL}posts/")
            existing_posts = response.json() if response.status_code == 200 else []

            if existing_posts:
                post_id = random.choice(existing_posts)["id"]
                like_post(post_id)
            else:
                print("⚠️ いいねできる投稿がないため、スキップ")

        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    bot_action()
