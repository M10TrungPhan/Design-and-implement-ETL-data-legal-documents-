import concurrent.futures
import os
import random
import threading
import time
from queue import Queue
from threading import Thread
import logging
from utils.utils import change_vpn


class Crawler(Thread):

    def __init__(self, search_key_service, item, number_crawler: int):
        super(Crawler, self).__init__()
        self.number_crawler = number_crawler
        self.item_web = item
        self.search_key_service = search_key_service
        self.path_save_data = self.search_key_service.path_save_data
        self.flag_finish = False
        self.flag_vpn = 0
        self.queue_item = Queue()
        self.logger = logging.getLogger(self.__class__.__name__)

    # GET ITEM IN QUEUES AND CRAWL
    def crawl(self):
        if not self.queue_item.qsize():
            return
        url = self.queue_item.get()
        item = self.item_web(url, self.search_key_service.keyword, self.path_save_data)
        status = ""
        if item.id in self.search_key_service.list_item_crawled:
            return

        try:
            status = item.extract_data()
        except Exception as error:
            print(error)
            print(item.url)
        try:
            item.driver.close()
        except:
            pass
        # CHECK WEBSITE BAN IP (FOR SHOPEE)
        if status == "VPN CHANGE":
            self.rotate_vpn()
            # change_vpn()
            return
        self.search_key_service.list_item_crawled.append(item.id)
        time.sleep(random.randint(5, 10))

    # CHANGE VPN IF WEBSITE BAN IP
    def rotate_vpn(self):
        if self.flag_vpn:
            return
        self.flag_vpn = 1
        change_vpn()
        self.flag_vpn = 0

    # def change_vpn(self):
    #     time.sleep(10)
    #     list_country = ["Viet nam", "Italy", "United States", "Spain", "Japan", "Taiwan", "Hong Kong"]
    #     country = random.choice(list_country)
    #     os.system("""nordvpn.lnk -c -g "{}" """.format(country))
    #     print(f"CONNECT VPN IN {country}")
    #     time.sleep(15)

    # GET LINK AND PUT TO QUEUE
    def manage_crawler(self):
        while True:
            if self.queue_item.qsize() < 2 * self.number_crawler:
                list_link = self.search_key_service.get_link_for_key()
                if list_link == "DONE":
                    self.flag_finish = True
                    break
                else:
                    for each in list_link:
                        self.queue_item.put(each)
            time.sleep(15)

    def thread_crawler(self):
        while True:
            if (not self.queue_item.qsize()) and (self.flag_finish == True):
                return

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.number_crawler) as executor:
                [executor.submit(self.crawl) for _ in range(self.number_crawler)]
            time.sleep(10)

    # CREATE FOLDER TO SAVE DATA
    def create_folder_save_data(self):
        os.makedirs(self.path_save_data, exist_ok=True)

    def run(self):
        self.create_folder_save_data()
        manage_crawler = threading.Thread(target=self.manage_crawler)
        manage_crawler.start()
        crawler = threading.Thread(target=self.thread_crawler)
        crawler.start()
        crawler.join()
        manage_crawler.join()

