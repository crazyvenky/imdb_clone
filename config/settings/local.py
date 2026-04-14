from .base import *

DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# You can add debug-toolbar here later without polluting base.py