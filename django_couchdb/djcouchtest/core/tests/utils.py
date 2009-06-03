import couchdb
from django.conf import settings


class CouchDBMock:
    def setup(self):
        self.server = couchdb.Server(settings.DATABASE_HOST)
        self.dbs = list(self.server)

    def teardown(self):
        for x in self.server:
            if not x in self.dbs:
                del self.server[x]
