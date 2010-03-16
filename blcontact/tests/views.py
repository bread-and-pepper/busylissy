from django.test import TestCase
from busylissy.blcontact.models import Contact
from busylissy.blproject.models import Project
from busylissy.blgroup.models import Group
from django.core.urlresolvers import reverse

class ViewTest(TestCase):

    fixtures = ['users.json', 'contacts.json', 'projects.json', 'groups.json']

    def test_detail(self):
        " Test detail page /contacts/<id>/ "
        user = self.client.login(username='john', password='doo')
        
        response = self.client.get(reverse('contact-detail', kwargs = {'id': 1 }))

        self.assertTemplateUsed(response, 'blcontact/detail.html')

                                   

     
