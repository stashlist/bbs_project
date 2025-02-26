from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from .models import Thread, Post, Tag

class CustomUserCreationForm(UserCreationForm):
    user_id = forms.CharField(
        max_length=50, 
        help_text="ログインに使用するユーザーIDを入力してください。",
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ("user_id", "username", "email", "password1", "password2")  # `user_id` を追加

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_id = self.cleaned_data["user_id"]
        if commit:
            user.save()
        return user

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]

class ThreadForm(forms.ModelForm):
    first_post_content = forms.CharField(
        label="最初の投稿",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=True,  # 必須入力
    )

    class Meta:
        model = Thread
        fields = ["title", "tags"]
        
    
    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        if not tags:
            raise forms.ValidationError("タグを選択してください。")
        return tags
        

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["avatar"]  # ユーザーが変更可能なフィールド


class SignupForm(UserCreationForm):
    email = forms.EmailField(label="メールアドレス", required=True)
    username = forms.CharField(label="ユーザー名", max_length=50, required=True)

    class Meta:
        model = CustomUser
        fields = ("user_id", "email", "username", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_verified = False  # 仮登録状態
        if commit:
            user.save()
        return user