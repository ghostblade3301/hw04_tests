from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create a non-authorized
        cls.guest_client = Client()
        # create an authorized client
        cls.user = User.objects.create_user(username='user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # create group in DB
        cls.group = Group.objects.create(
            title='Title for post',
            slug='test-slug',
            description='Description for group'
        )

        # create post in DB
        cls.post = Post.objects.create(
            text='Text for post',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def test_create_post(self):
        """При отправке валидной формы создается запись"""
        # amount of posts
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Text for post',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # checking redirect
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostCreateFormTests.user})
        )
        # checking amount of posts
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # checking existence of the new post
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group,
                text='Text for post').exists()
        )

    def test_create_post_guest(self):
        """Создание поста после авторизации"""
        # non-authorized client can't create a post
        form_data = {
            'text': 'Post from non-authorized client',
            'group': self.group.pk,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(
            Post.objects.filter(
                text='Post from non-authorized client').exists()
        )

    def test_edit_post_authorized(self):
        """Пост может редактировать создатель"""
        # authorized client can modify his post
        form_data = {
            'text': 'Post for test',
            'group': self.group.pk,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.group.pk)
        self.client.get(f'/posts/{post_edit.pk}/edit/')
        form_data = {
            'text': 'Edited post',
            'group': self.group.pk
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_edit.pk
                    }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.group.pk)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, 'Edited post')
