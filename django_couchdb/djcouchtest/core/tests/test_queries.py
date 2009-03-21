from django.core.management import call_command
from nose.tools import assert_equal

from djcouchtest.core.models import Boo

class TestQueries:
    def test_saveobject(self):
        call_command('syncdb', interactive=False, verbosity=0)
        b = Boo()
        b.title = "First Title"
        b.slug = "first_title"
        b.save()
        assert_equal(b.pk, 1)
