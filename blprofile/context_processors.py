from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.contrib.auth.models import User

from busylizzy.blprofile.models import UserProfile

def settings(request):
    """ Set the language correct for the user """
    language = translation.get_language_from_request(request)
    
    if request.user.is_authenticated():
        try:
            profile = request.user.get_profile()
        except ObjectDoesNotExist:
            profile = None
            
        if profile and profile.language != language:
            if profile.language in ["nl", "en"]:
                translation.activate(profile.language)
                request.LANGUAGE_CODE = translation.get_language()

    else:
        if language != request.LANGUAGE_CODE:
            translation.activate(request.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()
            
    return {
        'request': request,
        }
