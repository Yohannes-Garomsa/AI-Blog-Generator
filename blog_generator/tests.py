from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

class BlogGeneratorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_generator_blog_view(self):
        # A valid YouTube link
        youtube_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # The URL for the generator_blog view
        url = reverse('generator_blog')
        
        # The data to be sent in the POST request
        data = {'link': youtube_link}
        
        # Make the POST request
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        # Check that the response has a 200 status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains a 'content' key
        self.assertIn('content', response.json())
