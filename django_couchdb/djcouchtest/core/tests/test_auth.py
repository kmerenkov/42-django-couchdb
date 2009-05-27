from django.core.management import call_command
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from nose.tools import assert_equal
from couchdb import *


from djcouchtest.core.tests.utils import CouchDBMock

class TestAuthBackend(CouchDBMock):
    def test_syncdb(self):
        s = Server(settings.DATABASE_HOST)
        if 'auth_user' in s:
            del s['auth_user'] # can not use User.objects.all().delete() due to ManyToMany fields
        call_command('syncdb', interactive=False, verbosity=0)
        user = User.objects.create_user('foo', 'foo@gmail.com', 'foobardummy')
        user.save()
        new_user = authenticate(username='foo', password='foobardummy')
        assert new_user, "User can't be authenticated"
        assert_equal(user, new_user)

