from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post, Comment, Follow


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Заголовок тестовых данных',
            slug='group_test',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, который должен содержать хотя бы 15 символов'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий, который должен содержать 15 символов'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.post.author
        )

    def test_correct_objects_name(self):
        """Тестируем __str__ у моделей."""
        NUMBERS_OF_SYMBOL_IN_THE_TITLE = 15
        group = self.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

        post = self.post
        expected_post_name = post.text[:NUMBERS_OF_SYMBOL_IN_THE_TITLE]
        self.assertEqual(expected_post_name, str(post))

        comment = self.comment
        expected_comment_name = comment.text[:NUMBERS_OF_SYMBOL_IN_THE_TITLE]
        self.assertEqual(expected_comment_name, str(comment))

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Введи текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Выбери группу'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Поделись своим рецептом!',
            'group': 'К какой категории отнесем рецепт?'}
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
