from posts.models import Post, Comment, Group
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.user = User.objects.create(username='name')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        cache.clear()

    def test_create_post_authorised_user(self):
        """Валидная форма с картинкой создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст',
                     'image': self.post.image}
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'name'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data['text']).exists())

    def test_create_post_guest_user(self):
        """Неавторизованный пользователь не может создать запись в Post."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_post_authorised_and_guest_user(self):
        """Изменение поста автором и авторизованным пользователем."""
        form_data = {'text': 'Вносим изменения'}
        if self.user == self.post.author:
            response = self.authorised_client.post(
                reverse('posts:post_edit', kwargs={'post_id': '1'}),
                data=form_data,
                follow=True)
            self.assertRedirects(response,
                                 reverse('posts:post_detail',
                                         kwargs={'post_id': '1'}))
            self.assertTrue(Post.objects.filter(text=form_data
                                                ['text']).exists())
        elif self.user != self.post.author:
            response = self.authorised_client.post(
                reverse('posts:post_edit', kwargs={'post_id': '1'}),
                data=form_data,
                follow=True)
            self.assertFalse(Post.objects.filter(text=form_data
                                                 ['text']).exists())
        else:
            response = self.guest_client.get('/posts/1/edit/')
            self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_comment_auth_and_guest_user(self):
        """Комментирует пост только авторизованный пользователь."""
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

    @classmethod
    def tearDownClass(cls):
        """Удаляем директорию для временного хранения файлов."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
