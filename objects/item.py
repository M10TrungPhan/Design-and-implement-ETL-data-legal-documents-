import hashlib

# from config.config import Config


class Item:

    def __init__(self, url: str):
        self.url = url
        self._id = self.id
        # self.config = Config()

    @property
    def id(self):
        self._id = hashlib.md5(self.url.encode("utf-8")).hexdigest()
        return self._id
