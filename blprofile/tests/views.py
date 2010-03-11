from django.test import TestCase
from django.core.urlresolvers import reverse

class ViewTest(TestCase):
    """ Test the views for profiles """

    fixtures = ['users.json', 'profiles.json']

    def test_detail(self):
        """
        Test the detail page of user
        """
        response = self.client.get(reverse('profile-detail', kwargs = {'username': 'john'}))

        self.assertTemplateUsed(response, 'blprofile/detail.html')

        self.assertEqual(response.context["profile"].gender, 1)

    def test_user_not_exist(self):
        """
        Test User does not exist
        """
        reponse = self.client.get(reverse('profile-detail', kwargs = {'username': 'johnny'}))

        self.assertEqual(reponse.status_code, 404)

    def test_login_redirect(self):
        """
        Test login redirect
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('profile-view'))

        self.assertRedirects(response, reverse('profile-detail', kwargs = {'username': 'john'}), target_status_code=200)

    def test_delete_user(self):
        """
        Test delete the user and the profile
        """
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('profile-delete'))

        self.assertRedirects(response, reverse('busylizzy-home'), target_status_code=200)

        
