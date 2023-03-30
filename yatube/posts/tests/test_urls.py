from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.core.cache import cache


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый пост')
        cls.group = Group.objects.create(
            title='Заголовок теста',
            slug='group_test',
            description='Описание тестовой группы')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='HasNoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names_for_auth = {
            '/': 'posts/index.html',
            '/group/group_test/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for address, template in templates_url_names_for_auth.items():
            cache.clear()
            with self.subTest(address=address):
                response = self.authorised_client.get(address)
                self.assertTemplateUsed(response, template)
        templates_url_names_for_guest = {
            '/': 'posts/index.html',
            '/group/group_test/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names_for_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_open_page(self):
        """Тестирование общедоступных страниц."""
        context = ['/',
                   '/group/group_test/',
                   '/profile/auth/',
                   '/posts/1/']
        for address in context:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_authorized_user(self):
        """Страницы, доступные авторизованному пользователю."""
        context_status_ok = ['/create/',
                             '/follow/']
        for address in context_status_ok:
            with self.subTest(address=address):
                response = self.authorised_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        context_status_found = ['/profile/auth/follow/',
                                '/profile/auth/unfollow/',
                                '/posts/1/comment/']
        for address in context_status_found:
            with self.subTest(address=address):
                response = self.authorised_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_page_for_author(self):
        """Страница 'posts/<int:post_id>/edit/' доступна только автору."""
        if self.user == self.post.author:
            response = self.authorised_client.get('/posts/1/edit/',
                                                  follow=True)
            self.assertRedirects(response, '/posts/1/')
        elif self.user != self.post.author:
            response = self.guest_client.get('/posts/1/edit/')
            self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_unexisting_page(self):
        """Страница /test/ не существует."""
        response = self.authorised_client.get('/test/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
