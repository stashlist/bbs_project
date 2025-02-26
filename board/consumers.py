import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Post, Thread, IgnoredUsers
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from django.utils.timezone import localtime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.room_group_name = f"thread_{self.thread_id}"

        # WebSocket グループに参加
        if self.channel_layer is not None:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
        else:
            print("channel_layer is None! Check CHANNEL_LAYERS in settings.py")

        await self.accept()

    async def disconnect(self, close_code):
        # WebSocket グループから退出
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("🟢 WebSocket でメッセージを受信しました")
        data = json.loads(text_data)
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            return

        content = data["message"]
        thread = await sync_to_async(Thread.objects.get)(id=self.thread_id)

        # 投稿を作成
        post = await sync_to_async(Post.objects.create)(
            thread=thread,
            user=user,
            content=content
        )

        print(f"🟢 投稿を作成: ID={post.id}, 内容={post.content}")

        # **無視リストに登録されている場合は非表示メッセージを送信**
        ignored = await sync_to_async(IgnoredUsers.objects.filter(user=user, ignored_user=post.user).exists)()

        if ignored:
            message_content = "このレスは非表示の対象です。"
        else:
            message_content = post.content

        # **プロフィール画像を取得**
        avatar_url = await sync_to_async(user.get_profile_image)()

        # **日本時間でフォーマットを統一**
        formatted_time = localtime(post.created_at).strftime("%Y年%m月%d日 %H:%M")
        
        # **WebSocket グループ全員にメッセージを送信**
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": post.id,
                "username": user.username,
                "message": message_content,
                "created_at": formatted_time,  # **日本語形式の日時**
                "user_id": user.id,
                "avatar": avatar_url,  # **プロフィール画像のURLを追加**
                "parent_id": post.parent_id if post.parent_post else None
            }
        )

    async def chat_message(self, event):
        print("🟢 chat_message をクライアントに送信:", event)
        
        await self.send(text_data=json.dumps({
            "id": event["id"],
            "message": event["message"],
            "username": event["username"],
            "created_at": event["created_at"],  # **統一された日本語日時**
            "user_id": event["user_id"],
            "avatar": event["avatar"],  # **ここを追加**
            "parent_id": event.get("parent_id", None)  # **返信なら `parent_id` を送信**
        }))
