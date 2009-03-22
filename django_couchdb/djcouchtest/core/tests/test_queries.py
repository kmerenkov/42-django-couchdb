from django.core.management import call_command
from nose.tools import assert_equal

from djcouchtest.core.models import Boo, Foo

class TestQueries:
    def test_saveobject(self):
        call_command('syncdb', interactive=False, verbosity=0)
        Boo.objects.all().delete()
        Foo.objects.all().delete()
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
        f = Foo(boo=b)
        f.save()
        assert_equal(b.foo_set.count(), 1)
        assert_equal(b2.foo_set.count(), 0)
        f2 = Foo(boo=b2)
        f2.save()
        new_f = Foo.objects.filter(boo=b)[0]
        assert new_f.boo.title == "First Title"


