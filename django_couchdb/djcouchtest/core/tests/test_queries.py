from django.core.management import call_command
from django.db.models import Q
from nose.tools import assert_equal

from djcouchtest.core.models import Boo, Foo


class TestQueries:
    def test_save_and_get(self):
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

    def test_complicated_where(self):
        call_command('syncdb', interactive=False, verbosity=0)
        Boo.objects.all().delete()
        assert_equal(Boo.objects.all().count(), 0)
        b1 = Boo(title="1", slug="1")
        b1.save()
        b11 = Boo(title="11", slug="1")
        b11.save()
        b2 = Boo(title="2", slug="2")
        b2.save()
        assert_equal(Boo.objects.filter(slug="1").count(), 2)
        assert_equal(Boo.objects.filter(slug="1").filter(title="1").count(), 1)
        assert_equal(Boo.objects.filter(Q(title="1") | Q(title="2")).count(), 2)

    def test_joins(self):
        call_command('syncdb', interactive=False, verbosity=0)
        Boo.objects.all().delete()
        Foo.objects.all().delete()
        b1 = Boo(title="1", slug="1")
        b1.save()
        b11 = Boo(title="11", slug="1")
        b11.save()
        b2 = Boo(title="2", slug="2")
        b2.save()
        f1 = Foo(boo=b1)
        f1.save()
        f2 = Foo(boo=b2)
        f2.save()
        f3 = Foo(boo=b1,boo2=b2)
        f3.save()
        assert_equal(Foo.objects.filter(boo__title="1").count(), 2)
        assert_equal(Foo.objects.filter(boo__title="11").count(), 0)
        assert_equal(Foo.objects.filter(Q(boo__title="1") | Q(boo__slug="2")).count(), 3)

        assert_equal(Foo.objects.filter(Q(boo__title="1") & Q(boo2__title="2")).count(), 1)
        assert_equal(Foo.objects.filter(Q(boo__title="1") & Q(boo2__title="11")).count(), 0)



