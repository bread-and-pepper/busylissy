from django.test import TestCase

from busylizzy.blprofile.models import UserProfile

class ModelTest(TestCase):
    """ Test the models of the profile application """
    fixtures = ['users', 'profiles']
    
    def test_public(self):
        """ 
        Test if only public profiles are returned with
        ``Profile.objects.public()``
        
        """
        profiles = UserProfile.objects.public()
        for p in profiles:
            self.failUnlessEqual(p.is_public, True)
