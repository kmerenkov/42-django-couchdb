from django.core.management import call_command
from django.db.models import Q
from nose.tools import assert_equal

from djcouchtest.core.models import Boo, Foo


class TestCreation:
    def test_syncdb(self):
        call_command('syncdb', interactive=False, verbosity=0)
        from django.db import connection
        cursor = connection.cursor()
        assert "core_boo" in connection.introspection.get_table_list(cursor)
        assert "core_foo" in connection.introspection.get_table_list(cursor)
        description = connection.introspection.get_table_description(cursor, 'core_boo')
        assert description, "Description for core_boo must not be None"
        assert 'id' in description, description
        assert 'title' in description, description
        assert 'NOT NULL' in description['title']
        assert 'PRIMARY KEY' in description['id']
        assert_equal(description['UNIQUE'],[[u'title', u'slug']])
        description = connection.introspection.get_table_description(cursor, 'core_foo')
        assert description, "Description for core_foo must not be None"
        assert 'boo_id' in description, description
        assert_equal(description['REFERENCES'],[u'boo_id=core_boo', u'boo2_id=core_boo'])

    def test_fixtures(self):
        call_command('syncdb', interactive=False, verbosity=0)
        Boo.objects.all().delete()
        Foo.objects.all().delete()
        call_command('loaddata', 'test_fixtures.json', verbosity=0)
        assert_equal(Boo.objects.filter(slug="1").count(), 2)
        assert_equal(Foo.objects.filter(Q(boo__title="1") & Q(boo2__title="2")).count(), 1)
