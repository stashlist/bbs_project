from django.core.mail import send_mail
import random
from django.conf import settings

def generate_verification_code():
    """5桁のランダムな認証コードを生成"""
    return str(random.randint(10000, 99999))

def send_verification_email(user_email, verification_code):
    """認証コードをメールで送信"""
    subject = "【jelyfish】ログイン用認証コード"
    message = f"以下の認証コードを入力してください: {verification_code}"
    from_email = "noreply@example.com"  # 送信元メールアドレス

    send_mail(subject, message, from_email, [user_email])
