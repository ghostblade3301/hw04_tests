from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post, User

POSTS_COUNT = 12


class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create an non-authorized client
        cls.guest_client = Client()
        # create two authorized clients
        cls.user1 = User.objects.create(username='User1')
        cls.user2 = User.objects.create(username='User2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user1)
        cls.authorized_client.force_login(cls.user2)

        # create first group in DB
        cls.group1 = Group.objects.create(
            title='Title for group1',
            slug='test-slug-1',
            description='Description for group1'
        )
        # create second group in DB
        cls.group2 = Group.objects.create(
            title='Title for group2',
            slug='test-slug-2',
            description='Description for group2'
        )

        cls.post = Post.objects.create(
            text='Test text for user1 group1',
            author=cls.user1,
            group=cls.group1,
        )

        cls.post = Post.objects.create(
            text='Test text for user2 group2',
            author=cls.user2,
            group=cls.group2,
        )

        # create 15 posts in first group
        for post in range(15):
            cls.post = Post.objects.create(
                text='Posts of group1',
                author=cls.user1,
                group=cls.group1
            )

        # create 5 posts in second group
        for post in range(5):
            cls.post = Post.objects.create(
                text='Posts of group2',
                author=cls.user2,
                group=cls.group2,
            )

        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': cls.group1.slug}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': cls.user1}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}): (
                'posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/create.html',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}): (
                'posts/create.html'),
        }

    # checking templates and reverse names
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # checking the dictionary of the index page context
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

    # checking context of group_list
    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-1'})
        )
        self.assertIn('group', response.context)
        self.assertEqual(response.context['group'], self.group1)
        self.assertIn('page_obj', response.context)

    # checking context of profile template
    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'User1'})
        )
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], self.user1)
        self.assertIn('posts_count', response.context)
        self.assertIn('page_obj', response.context)
        self.assertEqual(response.context['author'], self.user1)

    # post_detail template is formed with the correct context
    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': (self.post.pk)})
        )
        self.assertIn('post', response.context)
        self.assertIn('post', response.context)
        self.assertIn('post', response.context)
        
    # template is formed with the correct context
    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # test context of post_edit
    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.post.pk,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class TestPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.amount_of_post_last_page = POSTS_COUNT % 10
        cls.amount_of_pages = POSTS_COUNT // 10

        # create user
        cls.user = User.objects.create(username='user')

        # create group for paginator
        cls.group = Group.objects.create(
            title='Test title',
            slug='test-slug',
            description='Test description',
        )

        # create authorized client
        cls.authorized_client = Client()

        # create posts
        for post in range(POSTS_COUNT):
            Post.objects.create(
                text=f'Test post number {post}',
                author=cls.user,
                group=cls.group,
            )

    def test_paginator(self):
        '''Проверка работы паджинации'''
        # pages to check
        pages = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        ]
        for reverse_obj in pages:
            with self.subTest(reverse_obj=reverse_obj):
                self.assertEqual(
                    len(self.authorized_client.get(reverse_obj).context.get('page_obj')), settings.POSTS_PER_PAGE)




    # сhecking the number of paginator posts is 10
    def test_paginator_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.POSTS_PER_PAGE)


        
