from django.test import TestCase
from django.core.urlresolvers import reverse

class GroupViewsTest(TestCase):
    """ Test all group views """
    fixtures = ['users.json', 'groups.json']
    
    def test_list(self):
        """
        Test list of groups
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('group-list'), target_status_code=200)
        
        self.assertTemplateUsed(response, 'blgroup/list.html')

    def test_group_detail(self):
        """
        Test detail of group
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('group-detail', kwargs = {'slug': 'broodenpeper'}))

        self.assertTemplateUsed(response, 'blgroup/detail.html')

        self.assertEqual(response.context["group"].name, "broodenpeper")

        self.assertEqual(len(response.context["group"].members.all()), 1)

    def test_delete_member(self):
        """
        Test delete member from group
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('group-member-delete', kwargs = {'model_slug': 'broodenpeper', 'member_slug': 'jane'}))

        self.assertRedirects(response, reverse('group-detail', kwargs ={'slug':'broodenpeper'}), target_status_code=200)
        
    def test_delete_group(self):
        """
        Test delete of group
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('group-delete', kwargs = {'slug': 'broodenpeper'}))

        self.assertRedirects(response, reverse('group-list'), target_status_code=200)
    
    def test_group_not_exist(self):
        """
        Test group does not exist
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('group-detail', kwargs = {'slug': 'johnenjane' }))

        self.assertEqual(response.status_code, 404) 

