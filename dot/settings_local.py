from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = []
DEBUG = True
# SECRET_KEY = 'django-insecure-@y**phwf-7(aou^!wj3rc$cfpncse#as=96q-ip@b)9(#ha$&&'
SECRET_KEY = 't$o.B<Vf}+K=2RQ#.X?@p*t1Z]LhT@j|o=KcK0;9*):0<5W_1kU8?.=jI-3oi-M'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'mydatabase',
#         'USER': 'mydatabaseuser',
#         'PASSWORD': 'mypassword',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }