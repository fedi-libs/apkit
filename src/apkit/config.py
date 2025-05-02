
from logging import Logger
import logging

from .store.base import BaseStore
from .store.kv.inmemory import InMemoryStore

from ._version import __version__

class Config:
    allow_private_ip: bool = False
    user_agent = f"apkit/{__version__}"
    max_redirects: int = 5
    kv: BaseStore = InMemoryStore()
    inbox_urls: list[str] = ["/inbox"]

    logger: Logger = logging.getLogger("apkit")

    def compile(self):
        """Compile inbox_urls, etc. into a usable format
        """
        urls = []
        for url in self.inbox_urls:
            urls.append(url.replace("{identifier}", r"[^/]+"))
        self.inbox_urls = urls