from celery.schedules import crontab
from .auto_poster import auto_post, auto_reply, auto_like, auto_create_thread

CELERY_BEAT_SCHEDULE = {
    "auto_post": {
        "task": "board.auto_poster.auto_post",
        "schedule": crontab(minute="*/15"),  # 15分ごとに投稿
    },
    "auto_reply": {
        "task": "board.auto_poster.auto_reply",
        "schedule": crontab(minute="*/10"),  # 10分ごとに返信
    },
    "auto_like": {
        "task": "board.auto_poster.auto_like",
        "schedule": crontab(minute="*/5"),  # 5分ごとにいいね
    },
    "auto_create_thread": {
        "task": "board.auto_poster.auto_create_thread",
        "schedule": crontab(hour="*/6"),  # 6時間ごとにスレッド作成
    }
}
