from django.test import TestCase

from django.test.utils import setup_test_environment

from django.test import Client

from django.contrib.auth.models import User

from django.core.urlresolvers import reverse

# Create your tests here.


class LoginMethodsTests(TestCase):

    def setUp(self):
        #create test user
        self.testUserName = "TestUser"
        self.testUserPassword = "TestPassword"
        User.objects.create_user(username=self.testUserName, password=self.testUserPassword)

    def test_login_empty(self):
        response = self.client.post('/login/') #post empty login
        loginErrorFlag = response.context['login_error'] #get error flag
        self.assertEqual(loginErrorFlag, True) #compare

    def test_login_wrong_credentials(self):
        #post wrong credentials
        response = self.client.post('/login/', {'username': 'TestWrongUser', 'password': 'TestWrongPassword'})
        loginErrorFlag = response.context['login_error'] #get error flag
        self.assertEqual(loginErrorFlag, True) #compare

    def test_login_wrong_user(self):
        #post wrong username with a valid password
        response = self.client.post('/login/', {'username': 'TestWrongUser', 'password': self.testUserPassword})
        loginErrorFlag = response.context['login_error'] #get error flag
        self.assertEqual(loginErrorFlag, True) #compare

    def test_login_wrong_password(self):
        #post wrong password
        response = self.client.post('/login/', {'username': self.testUserName, 'password': 'TestWrongPassword'})
        loginErrorFlag = response.context['login_error'] #get error flag
        self.assertEqual(loginErrorFlag, True) #compare

    def test_login_right_credentials(self):
        #post right credentials
        response = self.client.post('/login/', {'username': self.testUserName, 'password': self.testUserPassword})
        self.assertRedirects(response, reverse('subjects_display', kwargs={'userpage': self.testUserName}))
