from django.conf import settings
from copy import copy
from couchdb.client import ResourceNotFound


class ModelMeta(object):
    GET_META_VIEW = """
function (record) {
  if ((record.Type == "model_meta") && (record.model == "%s")) {
    emit(record._id, record);
  }
}
"""

    def __init__(self, server, model_name):
        self.server = server
        self.model_name = model_name
        self._db = None

    def _init_db(self):
        if self._db:
            return
        try:
            self._db = self.server[settings.DATABASE_NAME]
        except ResourceNotFound:
            self._db = self.server.create(settings.DATABASE_NAME)

    def get_meta(self):
        self._init_db()
        result = self._db.query(ModelMeta.GET_META_VIEW % (self.model_name))
        rows = result.rows
        if rows:
            return rows[0]
        return []

    def set_meta(self, meta):
        self._init_db()
        meta_ = copy(meta)
        meta_['Type'] = 'model_meta'
        meta_['model'] = self.model_name
        self._db.create(meta_)

