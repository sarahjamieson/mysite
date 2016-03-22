from django.contrib.auth import authenticate
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

user = authenticate(username='shjn', password='shjn00')
if user is not None:
    if user.is_active:
        print "User valid, active and authenticated."
    else:
        print "Password valid but account has been disabled."
else:
    print "Username and password incorrect."
