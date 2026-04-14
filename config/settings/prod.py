from .base import *

DEBUG = env.bool('DEBUG', default=False)

# env.list automatically splits the comma-separated string from .env into a Python list
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])