from django.core.management import call_command
from nose.tools import assert_equal

from djcouchtest.core.models import Boo

class TestQueries:
    def test_saveobject(self):
        call_command('syncdb', interactive=False, verbosity=0)
        Boo.objects.all().delete()
        assert_equal(Boo.objects.all().count(), 0)
        b = Boo()
        b.title = "First Title"
        b.slug = "first_title"
        b.save()
        b2 = Boo()
        b2.title = "Second Title"
        b2.slug = "second_title"
        b2.save()
        assert_equal(Boo.objects.all().count(), 2)
        assert_equal(Boo.objects.filter(slug="first_title").count(),1)
