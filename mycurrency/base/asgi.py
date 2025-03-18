"""
ASGI config for MyCurrency project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import sys

from django.core.asgi import get_asgi_application

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Adds 'backbase/' to Python path


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycurrency.base.settings')

application = get_asgi_application()
