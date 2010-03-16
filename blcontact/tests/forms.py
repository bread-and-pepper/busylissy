from django.test import TestCase

from busylissy.blcontact import forms

class FormTest(TestCase):
    """ Test all form functions """
    
    def test_contact_form(self):
        """
        Test 'ContactForm'
        """
        form = forms.ContactForm(data={'first_name': '',
                                       'last_name': '',
                                       'phone': '0612345678',
                                       'email': '',
                                       'lead': ''})
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['first_name'], [u"This field is required."])

        form = forms.ContactForm(data={'first_name': 'henk',
                                       'last_name': 'smenk',
                                       'phone': '0612345678',
                                       'email': 'henk@smenk.com',
                                       'lead': True})

        self.failUnless(form.is_valid())
