from django.core.management import call_command

class TestCreation:
    def test_syncdb(self):
        call_command('syncdb', interactive=False, verbosity=0)
        from django.db import connection
        cursor = connection.cursor()
        assert "core_boo" in connection.introspection.get_table_list(cursor)
        assert "core_foo" in connection.introspection.get_table_list(cursor)
        description = connection.introspection.get_table_description(cursor, 'core_boo')
        assert description, "Description must not be None"
