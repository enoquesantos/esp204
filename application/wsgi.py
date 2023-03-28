"""
WSGI config for gavos project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import sys
from os.path import dirname

from django.core.wsgi import get_wsgi_application

_CURRENT_DIR = dirname(__file__)
_CURRENT_PARENT_DIR = dirname(_CURRENT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django.settings')

sys.path.append(_CURRENT_DIR)
sys.path.append(_CURRENT_PARENT_DIR)

application = get_wsgi_application()
