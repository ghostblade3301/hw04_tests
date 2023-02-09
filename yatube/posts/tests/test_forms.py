from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

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

        cls.index_page = 'posts:index'
        cls.group_list_page = 'posts:group_list'
        cls.profile_page = 'posts:profile'
        cls.post_detail_page = 'posts:post_detail'
        cls.post_create_page = 'posts:post_create'
        cls.post_edit_page = 'posts:post_edit'

    def test_create_post_authorized(self):
        """При отправке валидной формы создается запись"""
        # amount of posts
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Text for post',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(self.post_create_page),
            data=form_data,
            follow=True
        )
        # checking redirect
        self.assertRedirects(response, reverse(
            self.profile_page, kwargs={'username': PostCreateFormTests.user})
        )
        # checking amount of posts
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # checking existence of the new post
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group_id, form_data['group'])

    def test_create_post_guest(self):
        """Неавторизованный не может создать пост"""
        # non-authorized client can't create a post
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Post from non-authorized client',
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            reverse(self.post_create_page),
            data=form_data,
            follow=True,
        )
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, redirect)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_authorized(self):
        """Пост может редактировать создатель"""
        # authorized client can modify his post
        form_data = {
            'text': 'Edited post',
            'group': self.group.pk
        }
        response_edit = self.authorized_client.post(
            reverse(self.post_edit_page, args=[self.post.id]),
            data=form_data,
            follow=True,)
        self.assertRedirects(
            response_edit,
            reverse(self.post_detail_page, kwargs={'post_id': self.post.id})
        )

        post_edit = Post.objects.get(pk=self.group.pk)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.group_id, form_data['group'])
