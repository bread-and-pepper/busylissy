from django.test import TestCase

from busylissy.blprofile import forms

class FormTest(TestCase):
    """ Test the forms for profiles """

    fixtures = ['users.json', 'profiles.json']

    def test_profile_form(self):
        """
        Test 'ProfileForm'
        """
        form = forms.ProfileForm(data={'first_name': '#$%^',
                                       'last_name': '',
                                       'email': '',
                                       'gender': '',
                                       'website': '',
                                       'birth_date': '1990-02-19',
                                       'about_me': '',
                                       'is_public': True,})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors["first_name"], [u"Can only contain letters and numbers"])

        form = forms.ProfileForm(data={'first_name': 'john',
                                       'last_name': 'doe',
                                       'email': 'john@doe.org',
                                       'gender': '1',
                                       'website': 'www.johndoe.org',
                                       'birth_date': '1990-02-19',
                                       'about_me': 'I john doe',
                                       'is_public': True,})

        self.failUnless(form.is_valid())

    def test_member_form(self):
        """
        Test 'MemberForm' member must be existent
        """
        form = forms.MemberForm(data={'username': 'johnny'})

        self.failIf(form.is_valid())
        self.assertEqual(form.errors["username"], [u"User does not exist."])

        form = forms.MemberForm(data={'username': 'jane'})

        self.failUnless(form.is_valid())
