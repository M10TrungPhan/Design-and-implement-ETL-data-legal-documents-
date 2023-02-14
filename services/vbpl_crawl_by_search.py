import logging
import requests
from bs4 import BeautifulSoup
from utils.utils import setup_selenium_firefox
import os


class VBPLCrawlBySearch:

    def __init__(self, keyword:str, path_save_data: str):
        self.logger = logging.getLogger(self.__class__.__name__)
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

    def get_keyword_encoded(self):
        key = "%20".join(self.keyword.split())
        if key == "":
            key_encode = ""
        else:
            key_encode = "keyword=" + key
        return key_encode

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

    def get_number_total_link(self):
        url = "https://vbpl.vn/VBQPPL_UserControls/Publishing_22/TimKiem/p_KetQuaTimKiemVanBan.aspx??type=0&s=0&" \
              "SearchIn=VBPQFulltext&{}&IsVietNamese=True&DivID=tabVB_lv1_01" \
              "&Page=1&DonVi=&RowPerPage=10".format(self.get_keyword_encoded())
        print(url)
        soup = self.request_html(url)
        if soup is None:
            return None
        total_link = int(soup.find("div", class_="message").find("strong").text)
        self.total_link = total_link
        return self.total_link

    def get_total_page(self):
        self.get_number_total_link()
        self.number_page = int(self.total_link / self.number_link_in_page)
        # print(f"NUMBER OF PAGE: {self.number_page}. EACH PAGE HAS {self.number_link_in_page} LINK")
        return self.number_page

    def get_link_in_page(self, page):
        url = "https://vbpl.vn/VBQPPL_UserControls/Publishing_22/TimKiem/p_KetQuaTimKiemVanBan.aspx??type=0&s=0&" \
              "SearchIn=VBPQFulltext&{}&IsVietNamese=True&DivID=tabVB_lv1_01" \
              "&Page={}&DonVi=&RowPerPage={}".format(self.get_keyword_encoded(), page, self.number_link_in_page)
        soup = self.request_html(url)
        list_link = []
        if soup is None:
            return list_link
        list_tag_link = soup.findAll("p", class_="title")
        for tag in list_tag_link:
            link = "https://vbpl.vn" + tag.find("a").get("href")
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


# a = VBPLCrawlBySearch("Chứng khoán")
# print(a.total_link, a.number_page)
# print(a.get_link_for_key())
# print(a.get_link_for_key())
