class BaseFakeModel(object):
    def __init__(self, name, meta=None):
        self.name = name
        self.meta = meta

    def get(self):
        pass

    def set(self):
        pass

    def update(self):
        pass

    def drop(self):
        pass

    def get_meta(self):
        return self.meta
