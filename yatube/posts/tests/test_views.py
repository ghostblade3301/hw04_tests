from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


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
        # create 15 posts in first group
        for post in range(15):
            cls.post = Post.objects.create(
                text='Posts of group1',
                author=cls.user1,
                group=cls.group1
            )

        # create 5 posts in first group
        for post in range(5):
            cls.post = Post.objects.create(
                text='Posts of group2',
                author=cls.user2,
                group=cls.group2
            )

    # checking templates and reverse names
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug-1'}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': 'User1'}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): (
                'posts/create.html'),

        }

        for reverse_name, template in templates_pages_names.items():
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

    # сhecking the number of paginator posts (10)
    def test_paginator_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    # test for second page of paginator; 5 posts of first group
    # and five posts of second
    def test_paginator_second_page_contains_five_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 10)

    # checking the amount of posts in second group (5)
    def test_paginator_group_list_contains_five_records(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-2'})
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    # checking the number of posts of the second user (5)
    def test_paginator_profile_contains_two_records(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'User2'})
        )
        self.assertEqual(len(response.context['page_obj']), 5)
