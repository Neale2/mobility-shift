from django.test import TestCase
from django.urls import reverse
from unittest import mock
from main.models import User, DeletedUser, Trip, DeletedTrip

# Testing Confirm page
class GetConfirmTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

    def test_at_location(self):
        response = self.client.get('/signup/confirm/')
        self.assertEqual(response.status_code, 200)

    def test_correct_template(self):
        response = self.client.get('/signup/confirm/')
        self.assertTemplateUsed(response, 'confirm.html')

        
# Testing Thanks page        
class GetThanksTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

    def test_at_location_yes(self):
        response = self.client.get('/yes/thanks/')
        self.assertEqual(response.status_code, 200)

    def test_correct_template_yes(self):
        response = self.client.get('/yes/thanks/')
        self.assertTemplateUsed(response, 'thanks.html')
        
    def test_at_location_no(self):
        response = self.client.get('/no/thanks/')
        self.assertEqual(response.status_code, 200)

    def test_correct_template_no(self):
        response = self.client.get('/no/thanks/')
        self.assertTemplateUsed(response, 'thanks.html')

        
# Testing Stillsubbed page
class GetStillSubbedTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

    def test_at_location(self):
        response = self.client.get('/unsubscribe/stillsubbed/')
        self.assertEqual(response.status_code, 200)

    def test_correct_template(self):
        response = self.client.get('/unsubscribe/stillsubbed/')
        self.assertTemplateUsed(response, 'stillsubbed.html')
        
        
# Testing Unsubbed page
class GetUnSubbedTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

    def test_at_location(self):
        response = self.client.get('/unsubscribe/unsubbed/')
        self.assertEqual(response.status_code, 200)

    def test_correct_template(self):
        response = self.client.get('/unsubscribe/unsubbed/')
        self.assertTemplateUsed(response, 'unsubbed.html')
        
        
#Testing SignUp page (get)
class GetSignUpTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

    def test_at_location(self):
        response = self.client.get('/signup/')

        self.assertEqual(response.status_code, 200)

    def test_correct_template(self):
        response = self.client.get('/signup/')
        self.assertTemplateUsed(response, 'signup.html')


class GetLogTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
        email='test@example.com',
        age_group='<13',
        gender='male',
        uuid='82c3a98d-13c6-4129-8ec1-725f592412d8'
        )
    
    def setUp(self):
        pass
    
    def test_at_location_yes(self):
        response = self.client.get('/yes/82c3a98d-13c6-4129-8ec1-725f592412d8')
        self.assertEqual(response.status_code, 200)
    
    def test_correct_template_yes(self):
        response = self.client.get('/yes/82c3a98d-13c6-4129-8ec1-725f592412d8')
        self.assertTemplateUsed(response, 'yes.html')
        
    def test_at_location_no(self):
        response = self.client.get('/no/82c3a98d-13c6-4129-8ec1-725f592412d8')
        self.assertEqual(response.status_code, 200)
    
    def test_correct_template_no(self):
        response = self.client.get('/no/82c3a98d-13c6-4129-8ec1-725f592412d8')
        self.assertTemplateUsed(response, 'no.html')
        
class GetUnsubscribeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
        email='test@example.com',
        age_group='<13',
        gender='male',
        uuid='82c3a98d-13c6-4129-8ec1-725f592412d8'
        )
    
    def setUp(self):
        pass
    
    def test_at_location(self):
        response = self.client.get('/unsubscribe/82c3a98d-13c6-4129-8ec1-725f592412d8')
        self.assertEqual(response.status_code, 200)
    
    def test_correct_template(self):
        response = self.client.get('/unsubscribe/82c3a98d-13c6-4129-8ec1-725f592412d8')
        self.assertTemplateUsed(response, 'unsub.html')
        
        
        
class PostSignupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass
    
    def setUp(self):
        pass
    
    @mock.patch('django_altcha.AltchaField.validate')
    @mock.patch('main.views.send_email')
    def test_response_code(self, email, validator):
        data = {
            'email': 'test@example.com',
            'age_group': '<13',
            'gender': 'male',
            'captcha': 'dummy'
        }
        response = self.client.post('/signup/', data)
        #redirect code
        self.assertEqual(response.status_code, 302)
        
    @mock.patch('django_altcha.AltchaField.validate')
    @mock.patch('main.views.send_email')
    def test_redirect(self, email, validator):
        data = {
            'email': 'test@example.com',
            'age_group': '<13',
            'gender': 'male',
            'captcha': 'dummy'
        }
        response = self.client.post('/signup/', data)
        self.assertEqual(response["Location"], 'confirm/')
        
    @mock.patch('django_altcha.AltchaField.validate')
    @mock.patch('main.views.send_email')
    def test_user_creation(self, email, validator):
        data = {
            'email': 'test@example.com',
            'age_group': '<13',
            'gender': 'male',
            'captcha': 'dummy'
        }
        response = self.client.post('/signup/', data)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        

    