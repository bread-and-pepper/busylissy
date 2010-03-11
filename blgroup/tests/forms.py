from django.test import TestCase

from busylizzy.blprofile.forms import MemberForm
from busylizzy.blgroup import forms

class GroupFormTest(TestCase):
    """ Test group forms """
    fixtures = ['users.json', 'groups.json']

    def test_group_form(self):
        """
        Test 'GroupForm'
        - group must be unique
        """
        form = forms.GroupForm(data={'name':'broodenpeper'})
        self.failIf(form.is_valid())

        self.assertEqual(form.errors['name'], [u"Group with this Name already exists."])

        form = forms.GroupForm(data={'name':''})
        self.failIf(form.is_valid())

        self.assertEqual(form.errors['name'], [u"This field is required."])

        form = forms.GroupForm(data={'name':'johnenjane'})

        self.failUnless(form.is_valid())

    def test_member_form(self):
        """
        Test 'MemberForm'
        - member must be existent
        """
        form = MemberForm(data={'username': 'bla'})

        self.failIf(form.is_valid())
        self.assertEqual(form.errors['username'], [u"Deze gebruiker bestaat niet."])

        form = MemberForm(data={'username':'jane'})

        self.failUnless(form.is_valid())

        
    
