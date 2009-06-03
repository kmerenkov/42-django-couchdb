from django.core.management import call_command
from nose.tools import assert_equal


class TestCreation:
    def test_syncdb(self):
        call_command('syncdb', interactive=False, verbosity=0)
        from django.db import connection
        cursor = connection.cursor()
        assert "core_boo" in connection.introspection.get_table_list(cursor)
        assert "core_foo" in connection.introspection.get_table_list(cursor)
        description = connection.introspection.get_table_description(
            cursor, 'core_boo')
        assert description, "Description for core_boo must not be None"
        assert 'id' in description, description
        assert 'title' in description, description
        assert 'NOT NULL' in description['title']
        assert 'PRIMARY KEY' in description['id']
        assert_equal(description['UNIQUE'],[[u'title', u'slug']])
        description = connection.introspection.get_table_description(
            cursor, 'core_foo')
        assert description, "Description for core_foo must not be None"
        assert 'boo_id' in description, description
        assert_equal(description['REFERENCES'],[u'boo_id=core_boo'])

