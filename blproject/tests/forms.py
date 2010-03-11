from django.test import TestCase

from busylizzy.blproject import forms

class FormTest(TestCase):

    fixtures = ['users.json', 'projects.json']

    def test_project_form(self):
        """
        Test 'ProjectForm' enforces to use unique project name
        """
        form = forms.ProjectForm(data={'name': '',
                                       'slug': 'website',
                                       'description': 'description',
                                       'members': [1],
                                       'status': '1'})

        self.failIf(form.is_valid())
        self.assertEqual(form.errors["name"], [u"This field is required."])

        form = forms.ProjectForm(data={'name':'Coding',
                                       'slug':'coding',
                                       'description': 'description',
                                       'members': [1],
                                       'status': '1'})

        self.failUnless(form.is_valid())
