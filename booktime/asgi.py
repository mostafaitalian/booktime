import os

import django
from channels.routing import get_default_application

os.environ("DJANGO_SETTINGS_MODULE", "booktime.settings")
django.setup()
application = get_default_application()