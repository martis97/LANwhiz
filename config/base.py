from LANwhiz.utils import Utilities


class BaseConfig():
    def __init__(self, connection, config):
        self.connection = connection
        self.config = config
        self.utils = Utilities(connection)
        