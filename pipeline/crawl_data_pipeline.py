import logging
import time

from utils.utils import setup_logging
from services.crawl_shopee_service_new import CrawlShopeeService
from config.config import Config


class CrawlData:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = Config()
        self.logger.info("Create Crawl data object")
        self.crawl_shopee = CrawlShopeeService()
        self.start_crawl()

    def start_crawl(self):
        self.logger.info("Start crawl data Shopee")
        self.crawl_shopee.start()

if __name__ == "__main__":
    config = Config()
    crawl_data = CrawlData()
