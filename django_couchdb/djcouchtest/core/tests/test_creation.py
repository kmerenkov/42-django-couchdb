from django.core.management import call_command


class TestCreation:
    def test_syncdb(self):
        call_command('syncdb', interactive=False, verbosity=0)
        assert True

