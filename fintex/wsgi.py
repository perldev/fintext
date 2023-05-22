"""
WSGI config for fintex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintex.settings')
print("import controller and notify dispetcher")
from exchange import controller

try:

    import uwsgi
    uwsgi.register_signal(97, "worker1", gather_chanel_data)
    uwsgi.add_timer(97, 120)
except:
    traceback.print_exc()

application = get_wsgi_application()
