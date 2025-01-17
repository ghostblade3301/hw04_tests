from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': ('Группа'),
            'text': ('Текст'),
            'image': ('Картинка')
        }

        help_texts = {
            'group': ('Выберите группу'),
            'text': ('Добавьте текст'),
            'image': ('Добавьте картинку')
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Добавьте комментарий',
        }
