from django.conf import settings

def variables(request):
	return {
		"JQUERY_URL" : settings.JQUERY_URL
	}