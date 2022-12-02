from django import forms
from django.forms import ModelForm
from posts.models import Post, Comment



class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", 'image']
        labels = {
            'group': 'Группа',
            'image': 'Изображение',
        }


class CommentForm(ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {
            'text': 'Текст комментария',
        }