from django.test import TestCase
from busylizzy.blproject.models import Project
from django.core.urlresolvers import reverse

class ViewTest(TestCase):

    fixtures = ['users.json', 'projects.json']

    def test_detail(self):
        " Detail page /projects/<project>/ "
        user = self.client.login(username='john', password='doo')
        
        response = self.client.get(reverse('project-detail', kwargs = {'slug': 'busy-lizzy'}))

        self.assertEqual(response.template[0].name, 'blproject/detail.html')

        self.assertEqual(response.context["project"].name, "Busy Lizzy")

        self.assertEqual(len(response.context["project"].members.all()), 1)

    def test_project_not_exist(self):
        " Project does not exist "
        user = self.client.login(username='john', password='doo')
        
        response = self.client.get(reverse('project-detail', kwargs = {'slug': 'test'}))

        self.assertEqual(response.status_code, 404)

    def test_list_projects(self):
        " Test list projects "
        user = self.client.login(username='john', password='doo')

        response = self.client.get(reverse('project-list'))
        
        self.assertEqual(len(Project.objects.all()), 1)

        self.assertEqual(response.template[0].name, 'blproject/project_list.html')

    def test_delete_project(self):
        " Delete project /projects/<project>/delete/ "
        user = self.client.login(username='john', password='doo')

        response = self.client.get(reverse('project-delete', kwargs = {'slug': 'busy-lizzy' }))

        self.assertEqual(len(Project.objects.all()), 0)
        
        self.assertRedirects(response, reverse('project-list'))

    def test_delete_member(self):
        " Delete member from group "
        self.client.login(username='john', password='doo')

        response = self.client.get(reverse('project-member-delete', kwargs = {'model_slug': 'busy-lizzy', 'member_slug': 'jane'}))

        self.assertRedirects(response, reverse('project-detail', kwargs = {'slug': 'busy-lizzy'}), target_status_code=200)

        
