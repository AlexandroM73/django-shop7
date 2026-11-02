from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

# ИСПРАВЛЕНО: абсолютные импорты вместо относительных
from courses.models import Course, Lesson, Subscription
from courses.serializers import LessonSerializer
from django.contrib.auth.models import Group

User = get_user_model()


class CourseAndLessonTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')

        self.moderator_group, _ = Group.objects.get_or_create(name='Moderator')
        self.user2.groups.add(self.moderator_group)

        self.course = Course.objects.create(title='Test Course', description='Desc', owner=self.user1)
        self.client = APIClient()

    def test_create_lesson_valid_link(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'course': self.course.id,
            'title': 'Valid Lesson',
            'video_link': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }
        response = self.client.post('/api/courses/lessons/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_create_lesson_invalid_link(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'course': self.course.id,
            'title': 'Bad Lesson',
            'video_link': 'https://example.com/video'
        }
        response = self.client.post('/api/courses/lessons/', data, format='json')
        self.assertEqual(response.status_code, 400)
        # Проверка текста ошибки (может отличаться, лучше проверить наличие ключа 'video_link')
        self.assertIn('video_link', response.data)

    def test_moderator_cannot_create_course(self):
        self.client.force_authenticate(user=self.user2)
        data = {'title': 'Blocked Course', 'description': 'Desc'}
        response = self.client.post('/api/courses/courses/', data, format='json')
        self.assertEqual(response.status_code, 403)


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sub_user', password='pass')
        self.course = Course.objects.create(title='Sub Course', description='Desc', owner=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_toggle_subscription(self):
        url = '/api/courses/toggle-subscription/'
        data = {'course': self.course.id}

        resp1 = self.client.post(url, data, format='json')
        self.assertEqual(resp1.status_code, 201)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        resp2 = self.client.post(url, data, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_serializer_has_flag(self):
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.get(f'/api/courses/courses/{self.course.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('is_subscribed'))
