# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import Group, Post, User


class TestPostsURLs(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # create non-authorized client
        cls.guest_client = Client()

        # create authorized client
        cls.user = User.objects.create(username='Test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # create post in DB
        cls.post = Post.objects.create(
            author=cls.user,
            id=100,
            text='Text for test',
        )

        # create group in DB
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )

        # test templates and pages
    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Test/': 'posts/profile.html',
            '/posts/100/': 'posts/post_detail.html',
            '/create/': 'posts/create.html',
            '/posts/100/edit/': 'posts/create.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
