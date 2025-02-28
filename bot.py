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


def create_thread(title, first_post):
    """スレッドを作成する"""
    response = session.post(
        f"{BASE_URL}api/threads/",
        json={"title": title, "first_post": first_post},
    )
    if response.status_code == 201:
        thread_id = response.json().get("id")
        print(f"✅ スレッド作成成功: ID={thread_id}")
        return thread_id
    else:
        print(f"❌ スレッド作成失敗: {response.status_code}, {response.json()}")
        return None




def create_post(thread_id, content):
    """スレッドに投稿"""
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


def get_posts():
    """ポスト一覧を取得する（POSTメソッド使用）"""
    try:
        response = session.post(f"{BASE_URL}posts/list/")  # リスト取得用のエンドポイント
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ ポスト一覧取得失敗: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(f"❌ ポスト一覧取得エラー: {e}")
        return []


def get_threads():
    """スレッド一覧を取得する（POSTメソッド使用）"""
    try:
        response = session.post(f"{BASE_URL}threads/list/")  # リスト取得用のエンドポイント
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ スレッド一覧取得失敗: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(f"❌ スレッド一覧取得エラー: {e}")
        return []


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
    

def reply_to_post(thread_id, post_id, reply_content):
    """投稿に返信をする"""
    response = session.post(f"{BASE_URL}posts/{post_id}/reply/", json={
        "thread_id": thread_id,
        "content": reply_content
    })

    if response.status_code == 201:
        print(f"💬 返信成功: {reply_content}（返信先 ID: {post_id}）")
        return response.json().get("id")
    else:
        print(f"❌ 返信失敗: {response.status_code}, {response.text}")
        return None


def bot_action():
    """Bot のアクションループ（行動割合を調整）"""
    login()

    while True:
        # 🎯 いいね: 50%、ポスト: 30%、返信: 15%、スレッド作成: 5%
        action = random.choices(
            ["like_post", "create_post", "reply_post", "create_thread"],
            weights=[50, 30, 15, 5]  # **行動割合を指定**
        )[0]

        if action == "create_thread":
            thread_title = generate_text("掲示板で自然に見えるスレッドタイトルを1つ考えてください。")
            first_post = generate_text("スレッドの最初の投稿内容を考えてください。")
            thread_id = create_thread(thread_title, first_post)
            if thread_id:
                time.sleep(5)  # **スレッド作成後、少し待つ**
                post_content = generate_text("スレッド作成後に最初の投稿を追加してください。")
                create_post(thread_id, post_content)

        elif action == "create_post":
            existing_threads = get_threads()  # 修正：get_threads関数を使用

            # **スレッドがない場合、新しく作成**
            if not existing_threads:
                print("⚠️ スレッドがないため、新規スレッドを作成")
                thread_title = generate_text("掲示板で自然に見えるスレッドタイトルを1つ考えてください。")
                first_post = generate_text("スレッドの最初の投稿内容を考えてください。")
                thread_id = create_thread(thread_title, first_post)
                time.sleep(5)
                create_post(thread_id, first_post)
            else:
                thread_id = random.choice(existing_threads)["id"]
                post_content = generate_text("掲示板の流れに自然な投稿を1つ考えてください。")
                create_post(thread_id, post_content)

        elif action == "reply_post":
            existing_posts = get_posts()  # 修正：get_posts関数を使用

            if not existing_posts:
                print("⚠️ ポストがないため、新規投稿を作成")
                existing_threads = get_threads()  # 修正：get_threads関数を使用
                if not existing_threads:
                    print("⚠️ スレッドもないため、新規スレッドを作成")
                    thread_title = generate_text("掲示板で自然に見えるスレッドタイトルを1つ考えてください。")
                    first_post = generate_text("スレッドの最初の投稿内容を考えてください。")
                    thread_id = create_thread(thread_title, first_post)
                    time.sleep(5)
                    create_post(thread_id, first_post)
                else:
                    thread_id = random.choice(existing_threads)["id"]
                    post_content = generate_text("掲示板の流れに自然な投稿を1つ考えてください。")
                    create_post(thread_id, post_content)
            else:
                try:
                    post = random.choice(existing_posts)
                    if "id" in post and "thread_id" in post and "content" in post:
                        post_id = post["id"]
                        thread_id = post["thread_id"]
                        reply_content = generate_text(f"「{post['content']}」に対する自然な返信を考えてください。")
                        reply_to_post(thread_id, post_id, reply_content)
                    else:
                        print("⚠️ ポストデータに必要なフィールドがありません")
                        # フォールバック：スレッドを取得して新規投稿
                        existing_threads = get_threads()
                        if existing_threads:
                            thread_id = random.choice(existing_threads)["id"]
                            post_content = generate_text("掲示板の流れに自然な投稿を1つ考えてください。")
                            create_post(thread_id, post_content)
                except (IndexError, KeyError) as e:
                    print(f"⚠️ ポストデータ処理エラー: {e}")

        elif action == "like_post":
            existing_posts = get_posts()  # 修正：get_posts関数を使用
            
            if existing_posts and isinstance(existing_posts, list) and len(existing_posts) > 0:
                try:
                    # ポストに"id"キーがあるか確認
                    if "id" in existing_posts[0]:
                        post_id = random.choice(existing_posts)["id"]
                        like_post(post_id)
                    else:
                        print("⚠️ ポストの形式が不正です。'id'フィールドがありません。")
                except (IndexError, KeyError) as e:
                    print(f"⚠️ ポストデータ処理エラー: {e}")
            else:
                print("⚠️ いいねを押すポストがないため、スキップ")

        # ⏳ **投稿の間隔をランダムに調整**
        sleep_time = random.randint(10, 60)  # 10秒〜60秒の間でランダム
        print(f"⏳ 次のアクションまで {sleep_time} 秒待機")
        time.sleep(sleep_time)


if __name__ == "__main__":
    bot_action()