import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
from board.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack  # 追加

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bbs_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # 認証情報を WebSocket に渡す
        URLRouter(websocket_urlpatterns)
    ),
})


# 明示的にチャンネルレイヤーを作成
channel_layer = get_channel_layer()
