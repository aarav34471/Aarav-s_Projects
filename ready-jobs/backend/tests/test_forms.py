
from django.test import TestCase
from core.forms import RegistrationForm

class RegistrationFormTest(TestCase):
    def test_valid_form(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123'
        })
        self.assertTrue(form.is_valid())
