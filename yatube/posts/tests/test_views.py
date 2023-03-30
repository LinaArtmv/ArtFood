from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group, Follow, Comment
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache


User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок теста',
            slug='group_test',
            description='Описание тестовой группы')
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B")
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif")
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        """Удаляем директорию для временного хранения файлов."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='HasNoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names_for_auth = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'group_test'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'}
        for reverse_name, template in templates_pages_names_for_auth.items():
            cache.clear()
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        templates_pages_names_for_guest = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'group_test'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html'}
        for reverse_name, template in templates_pages_names_for_guest.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_correct_context(self):
        """Шаблоны index, group_list, profile с правильным контекстом."""
        responses = {(reverse('posts:index')): 'post_list',
                     (reverse('posts:group_list',
                              kwargs={'slug': 'group_test'})): 'posts',
                     (reverse('posts:profile',
                              kwargs={'username': 'auth'})): 'post_list'}
        for response, object in responses.items():
            first_obj = self.authorised_client.get(response).context[object][0]
            post_text_0 = first_obj.text
            post_group_0 = first_obj.group
            post_image_0 = first_obj.image
            self.assertEqual(post_image_0, self.post.image)
            self.assertEqual(post_text_0, 'Тестовый пост')
            self.assertEqual(post_group_0, self.group)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorised_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id': '1'}))
        first_obj = response.context['post']
        post_text_0 = first_obj.text
        post_group_0 = first_obj.group
        post_image_0 = first_obj.image
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_form_create_post(self):
        """Шаблон post_create c правильной формой."""
        response = self.authorised_client.get(reverse('posts:post_create'))
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_work_follow_index(self):
        """На странице follow/ появляются корректные посты."""
        self.authorised_client.get('/profile/auth/follow/')
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.post.author).exists())
        response = self.authorised_client.get(reverse('posts:follow_index'))
        first_obj = response.context['post_list'][0]
        post_author = first_obj.author
        self.assertEqual(post_author, self.post.author)
        self. authorised_client.get('/profile/auth/unfollow/')
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.post.author).exists())

    def test_display_post_on_page(self):
        """Пост с группой отображается в index, group_list, profile."""
        form_fields = {reverse('posts:index'):
                       Post.objects.get(group=self.post.group),
                       reverse('posts:group_list',
                               kwargs={'slug': 'group_test'}):
                       Post.objects.get(group=self.post.group),
                       reverse('posts:profile', kwargs={'username': 'auth'}):
                       Post.objects.get(group=self.post.group)}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorised_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    def test_check_group_not_in_mistake_group_list_page(self):
        """Проверяем что пост не попал в чужую группу."""
        form_fields = {reverse('posts:group_list',
                               kwargs={'slug': self.group.slug}):
                       Post.objects.exclude(group=self.post.group)}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorised_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_cache(self):
        """Проверка работы кэша."""
        reply_1 = self.guest_client.get(reverse('posts:index'))
        response_1 = reply_1.content
        Post.objects.get(id=1).delete()
        reply_2 = self.guest_client.get(reverse('posts:index'))
        response_2 = reply_2.content
        self.assertEqual(response_1, response_2)

    def test_auth_user_can_follow_on_the_other_users(self):
        """Способность подписки и отписки от других пользователей."""
        self.authorised_client.get('/profile/auth/follow/')
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.post.author).exists())
        self.authorised_client.get('/profile/auth/unfollow/')
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.post.author).exists())
        response = self.guest_client.get('/profile/auth/follow/')
        self.assertRedirects(response,
                             '/auth/login/?next=/profile/auth/follow/')
        response = self.guest_client.get('/profile/auth/unfollow/')
        self.assertRedirects(response,
                             '/auth/login/?next=/profile/auth/unfollow/')
        if self.user == self.post.author:
            self.authorised_client.get('/profile/auth/follow/')
            self.assertFalse(Follow.objects.filter(
                user=self.user, author=self.post.author).exists())

    def test_comment_auth_and_guest_user(self):
        """Комментирует пост только авторизованный пользователь и автор."""
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorised_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response_guest,
                             '/auth/login/?next=/posts/1/comment/')
        if self.user == self.post.author:
            response_author = self.authorised_client.post(
                reverse('posts:add_comment', kwargs={'post_id': '1'}),
                data=form_data,
                follow=True)
            self.assertRedirects(response_author, reverse(
                'posts:post_detail', kwargs={'post_id': '1'}))

    def test_comment_show_on_the_posts_pages(self):
        """Комментарий отображается на странице поста."""
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorised_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True)
        self.assertTrue(Comment.objects.filter(
            text=form_data['text'], post=1).exists())
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем запись в БД."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок теста',
            slug='group_test',
            description='Описание тестовой группы')
        cls.posts = [
            Post(
                author=cls.user,
                text=f'Тестовый пост{i}',
                group=cls.group,)
            for i in range(13)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        """Создаем авторизованного и неавторизованного клиента."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_first_page_of_paginator(self):
        """Паджинация первой страницы."""
        cache.clear()
        NUMBERS_OF_POSTS_IN_THE_FIRST_PAGE: int = 10
        urls = {reverse('posts:index'),
                reverse('posts:group_list', kwargs={'slug': 'group_test'}),
                reverse('posts:profile', kwargs={'username': 'auth'})}
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']),
                             NUMBERS_OF_POSTS_IN_THE_FIRST_PAGE)

    def test_second_page_of_paginator(self):
        """Паджинация последней страницы."""
        NUMBERS_OF_POSTS_IN_THE_LAST_PAGE: int = 3
        urls = {reverse('posts:index'),
                reverse('posts:group_list', kwargs={'slug': 'group_test'}),
                reverse('posts:profile', kwargs={'username': 'auth'})}
        for url in urls:
            response = self.client.get((url) + '?page=2')
            self.assertEqual(len(response.context['page_obj']),
                             NUMBERS_OF_POSTS_IN_THE_LAST_PAGE)
