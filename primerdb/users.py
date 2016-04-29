from django.contrib.auth import authenticate
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from django.contrib.auth.models import User


def add_user():
    username = raw_input('Enter new username: ')
    password = raw_input('Enter new password: ')
    user = User.objects.create_user(username=username, password=password)
    user.save()
    authenticate_user(username, password)


def authenticate_user(username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            print "User valid, active and authenticated."
        else:
            print "Password valid but account has been disabled."
    else:
        print "Username and password incorrect."


def change_password():
    username = raw_input('Enter existing username: ')
    password = raw_input('Enter new password: ')
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()


def list_all_users():
    users = User.objects.all()
    print users

change_password()