from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post


class TestIndexPage(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_index_available(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TestGroups(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def tearDown(self) -> None:
        Group.objects.filter().delete()

    def test_page_not_found(self):
        response = self.client.get("/group/not_exist/")
        self.assertEqual(response.status_code, 404)

    def test_exists_group(self):
        Group.objects.create(
            title="test",
            slug="first_group2",
            description="description first_group",
        )
        response = self.client.get("/group/first_group2/")
        self.assertEqual(response.status_code, 200)


class TestPost(TestCase):
    def setUp(self) -> None:
        User.objects.filter(username="test_user").delete()
        self.auth_client = Client()
        user = User.objects.create_user(username="test_user", email="q@q.com")
        user.set_password("123")
        user.save()
        self.auth_client.login(username="test_user", password=123)

    def tearDown(self) -> None:
        Group.objects.filter(
            title="test",
            slug="first_group",
            description="description first_group",
        ).delete()

        User.objects.filter(username="test_user").delete()

    def test_valid_form(self):
        group = Group.objects.create(
            title="test",
            slug="first_group",
            description="description first_group",
        )
        group_id = f"{group.id}"
        self.auth_client.post(
            "/new/",
            data={
                "text": "test text",
                "group": group_id,
            },
        )

        self.assertTrue(Post.objects.filter(text="test text", group=group.id).exists())

    def test_form_not_valid(self):
        response = self.auth_client.post("/new/", data={"group": "100500"})

        self.assertFormError(
            response, form="form", field="text", errors=["Обязательное поле."]
        )


class TestStringMethod(TestCase):
    def test_length(self):
        self.assertEqual(len("BGG"), 3, msg="У вас ошибочка")


class TestProfileCreate(TestCase):
    def setUp(self) -> None:
        self.username = "LenaTest"
        self.email = "testuser@ya.ru"
        self.first_name = "Lena"
        self.last_name = "Dubovenko"
        self.password = "pa5ss1wor4d"

    def tearDown(self) -> None:
        User.objects.filter(username=self.username).delete()
        Post.objects.all().delete()

    def test_signup_page_url(self):
        response = self.client.get("/auth/signup/")
        self.assertEqual(response.status_code, 200, msg="Статус код != 200")
        self.assertTemplateUsed(response, "signup.html")

    def test_signup_form(self):
        response = self.client.post(
            reverse("signup"),
            data={
                "first_name": self.first_name,
                "last_name": self.last_name,
                "username": self.username,
                "email": self.email,
                "password1": self.password,
                "password2": self.password,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200, msg="Статус код != 200")

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1, msg="Пользователь не добавлен в БД")
        response = self.client.get(f"/{self.username}/")
        self.assertEqual(
            response.status_code, 200, msg="Страница нового пользователя не найдена"
        )

    def test_create_post(self):
        user = User.objects.create_user(username=self.username, password=self.password)
        self.client.force_login(user)
        response = self.client.get("/new/")
        self.assertEqual(response.status_code, 200)

    def test_no_create_post(self):
        response = self.client.get("/new/")
        self.assertRedirects(response, "/auth/login/?next=/new/")

    def test_appearance_new_record(self):
        cache.clear()
        text = "New world order"
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        self.client.force_login(user)
        post = Post.objects.create(
            text=text,
            pub_date=dt.now(),
            author=user,
            group=None,
        )
        response = self.client.get("/")
        self.assertContains(response, text)
        response = self.client.get(rf"/{self.username}/")
        self.assertContains(response, text)
        response = self.client.get(rf"/{self.username}/1/")
        self.assertContains(response, text)

    def test_correct_post_editing(self):
        cache.clear()
        text = "New world order"
        new_text = "Alabama is not Russia"
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        self.client.force_login(user)
        post = Post.objects.create(
            text=text,
            pub_date=dt.now(),
            author=user,
            group=None,
        )
        response = self.client.post(
            rf"/{self.username}/1/edit/",
            data={
                "text": new_text,
            },
        )
        response = self.client.get("/")
        self.assertContains(response, new_text)
        self.assertNotContains(response, text)
        response = self.client.get(rf"/{self.username}/")
        self.assertContains(response, new_text)
        self.assertNotContains(response, text)
        response = self.client.get(rf"/{self.username}/1/")
        self.assertContains(response, new_text)
        self.assertNotContains(response, text)

    def test_page_not_found(self):
        response = self.client.get("/yuiejfnhsadaywada/999999/")
        self.assertEqual(response.status_code, 404)


class TestImage(TestCase):
    def setUp(self) -> None:
        self.username = "LenaTest"
        self.email = "testuser@ya.ru"
        self.first_name = "Lena"
        self.last_name = "Dubovenko"
        self.password = "pa5ss1wor4d"
        self.text = "Random text fialka"

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        self.group = Group.objects.create(
            title="Иван Дрон",
            slug="first_group2",
            description="description first_group",
        )
        self.client.force_login(self.user)
        with open("media/file.jpg", "rb") as img:
            self.post = self.client.post(
                "/new/",
                {
                    "author": self.user,
                    "text": self.text,
                    "group": self.group.id,
                    "image": img,
                },
                follow=True,
            )

    def tearDown(self) -> None:
        User.objects.all().delete()
        Group.objects.all().delete()
        Post.objects.all().delete()

    def test_check_image_post(self):
        response = self.client.get(rf"/{self.user.username}/1/")
        self.assertContains(response, r"<img")

    def test_check_image_of_page(self):
        cache.clear()
        urls = ["/", f"/group/{self.group.slug}/", f"/{self.user}/"]
        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, r"<img")

    def test_check_image_dowloand(self):
        Post.objects.all().delete()
        with open("media/test.txt", "rb") as img:
            self.post = self.client.post(
                "/new/",
                {
                    "author": self.user,
                    "text": self.text,
                    "group": self.group.id,
                    "image": img,
                },
                follow=True,
            )
            response = self.client.get(f"/{self.user}/")
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, r"<img")

class TestCache(TestCase):
    def setUp(self) -> None:
        self.username = "LenaTest"
        self.email = "testuser@ya.ru"
        self.first_name = "Lena"
        self.last_name = "Dubovenko"
        self.password = "pa5ss1wor4d"
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
        )
        self.client.force_login(user)
        post = Post.objects.create(
            text="oh my ZH",
            pub_date=dt.now(),
            author=user,
            group=None,
        )

    def test_check_cache(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "oh my ZH")
        self.assertEqual(Post.objects.all().count(), 1)
        Post.objects.all().delete()
        response = self.client.get('/')
        self.assertEqual(Post.objects.all().count(), 0)
        self.assertContains(response, "oh my ZH")
        cache.clear()
        response = self.client.get('/')
        self.assertNotContains(response, "oh my ZH")