import concurrent.futures
import json
import logging
import re
import os

import requests
from bs4 import BeautifulSoup

from utils.utils import setup_selenium_firefox


class NHPLCrawlBySearch:

    def __init__(self, keyword: str, path_save_data):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.origin = "https://nganhangphapluat.lawnet.vn/"
        self.keyword = keyword
        self.path_save_data = path_save_data
        self.list_item_crawled = []
        self.list_link = []
        self.total_link = 0
        self.number_page = 0
        self.page_current = 1
        self.number_link_in_page = 30
        self.load_list_item_crawled()
        self.get_total_page()
        self.create_folder_save_data()

    def create_folder_save_data(self):
        path_text = self.path_save_data + "text/"
        os.makedirs(path_text, exist_ok=True)
        path_attached = self.path_save_data + "vpbl_attached/"
        os.makedirs(path_attached, exist_ok=True)

    def get_keyword_encoded(self):
        return "%20".join(self.keyword.split())

    @staticmethod
    def request_html(url):
        res = None
        for _ in range(5):
            try:
                res = requests.get(url)
                break
            except Exception as e:
                print(e)
                res = None
                continue
        if res is None:
            driver = setup_selenium_firefox()
            try:
                driver.get(url)
                res = driver.page_source
                driver.close()
            except Exception as e:
                print(e)
            if res is None:
                return None
        soup = BeautifulSoup(res.text, "lxml")
        return soup

    def get_total_page(self):
        url = "{}?kw={}&lvid=0&page=1&pageSize={}".format(self.origin, self.get_keyword_encoded(), self.number_link_in_page)
        soup = self.request_html(url)
        if soup is None:
            return None
        box_total_page = soup.find("div", attrs={"style": "text-align :center;height: 40px;line-height :40px;"})
        if box_total_page is not None:
            text = box_total_page.text
            (start, end) = re.search("của", text).span()
            self.number_page = int(text[end+1:])
        else:
            self.number_page = 0
        return self.number_page

    def get_link_in_page(self, page):
        url = "{}?kw={}&lvid=0&page={}&pageSize={}".format(self.origin, self.get_keyword_encoded(),
                                                           page, self.number_link_in_page)
        soup = self.request_html(url)
        list_link = []
        if soup is None:
            return list_link
        list_tag_link = soup.findAll("div", class_="item masterTooltip")
        for tag in list_tag_link:
            link = "https://nganhangphapluat.lawnet.vn" + tag.find("a", class_="tieu-de").get("href")
            list_link.append(link)
        return list_link

    def get_link_for_key(self):
        if self.page_current <= self.number_page:
            list_link = self.get_link_in_page(self.page_current)
            self.page_current += 1
            return list_link
        else:
            return "DONE"

    def load_list_item_crawled(self):
        file_data_folder = self.path_save_data + "text/"
        if os.path.exists(file_data_folder):
            list_item = os.listdir(file_data_folder)
            self.list_item_crawled = [item.replace(".json", "") for item in list_item]
        else:
            self.list_item_crawled = []
        return self.list_item_crawled
#
# a = NHPLCrawlBySearch("Chứng khoán")
# print(a.get_total_page())
# print(a.get_link_for_key())
# print(a.get_link_for_key())

