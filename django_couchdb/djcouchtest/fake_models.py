from django_couchdb.backends.couchdb.fake_model import BaseFakeModel


class FakeAuthPermission(BaseFakeModel):
    def __init__(self):
        super(FakeAuthPermission, self).__init__('auth_permission')
        self.meta = {'UNIQUE': [('content_type', 'codename')],
                     'codename': ['NOT NULL'],
                     'content_type_id': ['NOT NULL'],
                     'id': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     'name': ['NOT NULL'],
                     }

    def get(self):
        return []


class FakeAdminLog(BaseFakeModel):
    def __init__(self):
        super(FakeAdminLog, self).__init__('django_admin_log')
        self.meta = {'action_flag': ['NOT NULL'],
                     'action_time': ['NOT NULL'],
                     'change_message': ['NOT NULL'],
                     'content_type_id': None,
                     'id': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     'object_id': None,
                     'object_repr': ['NOT NULL'],
                     'user_id': ['NOT NULL'],
                     }

    def get(self):
        return []


class FakeAuthGroup(BaseFakeModel):
    def __init__(self):
        super(FakeAuthGroup, self).__init__('auth_group')
        self.meta = {'id': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     'name': ['NOT NULL', 'UNIQUE'],
                     }

    def get(self):
        return []


class FakeAuthMessage(BaseFakeModel):
    def __init__(self):
        super(FakeAuthMessage, self).__init__('auth_message')
        self.meta = {'id': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     'message': ['NOT NULL'],
                     'user_id': ['NOT NULL'],
                     }

    def get(self):
        return []


class FakeSite(BaseFakeModel):
    def __init__(self):
        super(FakeSite, self).__init__('django_site')
        self.meta = {'id': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     'name': ['NOT NULL'],
                     }

    def get(self):
        return []


class FakeSession(BaseFakeModel):
    def __init__(self):
        super(FakeSession, self).__init__('django_session')
        self.meta = {'id': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     'expire_date': ['NOT NULL'],
                     'session_data': ['NOT NULL'],
                     'session_key': ['PRIMARY KEY', 'NOT NULL', 'UNIQUE'],
                     }

    def get(self):
        return []
