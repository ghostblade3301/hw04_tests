from django.forms import ModelForm

from .models import Post


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
