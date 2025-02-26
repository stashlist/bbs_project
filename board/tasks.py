from celery import shared_task
from django.utils import timezone
from board.models import Thread

@shared_task
def delete_inactive_threads():
    ten_minutes_ago = timezone.now() - timezone.timedelta(minutes=10)

    # **最後の投稿が10分以上前のスレッドを取得**
    threads_to_delete = Thread.objects.filter(last_activity__lt=ten_minutes_ago)

    count = threads_to_delete.count()
    if count > 0:
        print(f"🟢 {count} 個のスレッドを削除しました")
        threads_to_delete.delete()

    return f"Deleted {count} inactive threads."
