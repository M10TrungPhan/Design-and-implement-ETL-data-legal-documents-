import re
import time
import json
import os
import hashlib

import requests
from utils.utils import setup_selenium_firefox
from bs4 import BeautifulSoup

from objects.item import Item


class ItemVBPL(Item):

    def __init__(self, url: str, keywords: str, path_save_data: str):
        super(ItemVBPL, self).__init__(url)
        self.url = url
        self.path_save_data = path_save_data
        self.keywords = keywords
        self.standard_id()
        self.html = None
        self.data = None
        self.attr = None
        self.digital_text = False
        self.pdf = False
        self.pdf_dir = None
        self.content = None

    def standard_id(self):
        if re.search("&Keyword=", self.url) is not None:
            start, end = re.search("&Keyword=", self.url).span()
            self.url = self.url[0:end]
            self._id = hashlib.md5(self.url.encode("utf-8")).hexdigest()
            return self._id

    def create_folder_save_data(self):
        path_pdf = self.path_save_data + "pdf/"
        os.makedirs(path_pdf, exist_ok=True)
        path_text = self.path_save_data + "text/"
        os.makedirs(path_text, exist_ok=True)

    def get_html(self):
        res = None
        for i in range(5):
            try:
                res = requests.get(self.url)
                break
            except Exception as e:
                print(e)
                res = None
                continue
        if res is None:
            driver = setup_selenium_firefox()
            try:
                driver.get(self.url)
                res = driver.page_source
                driver.close()
            except:
                pass
        if res is None:
            self.html = None
            return self.html
        self.html = BeautifulSoup(res.text, "lxml")
        return self.html

    def is_digital(self):
        if self.html.find("b", class_="fulltext") is not None:
            self.digital_text = True
        else:
            self.digital_text = False
        return self.digital_text

    def is_pdf(self):
        if self.html.find("b", class_="source"):
            self.pdf = True
        else:
            self.pdf = False
        return self.pdf

    def get_attr(self):
        list_attr = []
        tag_attr = self.html.find("div", class_="vbInfo")
        if tag_attr is not None:
            list_tag_att = tag_attr.findAll("li")
            for tag in list_tag_att:
                text = tag.text
                if text is None:
                    continue
                search = re.search("\r\n", text)
                if search is None:
                    continue
                (start, end) = search.span()
                name_att = text[0:start].rstrip()
                if name_att == "":
                    name_att = "Name"
                value_att = text[end:].strip()
                list_attr.append({name_att: value_att})
            self.attr = list_attr
            return self.attr
        else:
            self.attr = None
            return self.attr

    def get_content(self):
        self.content = self.html.find("div", class_="vbInfo").find_next_sibling().text
        return self.content

    def get_pdf_link(self):
        driver = setup_selenium_firefox()
        driver.get(self.url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "lxml")
        tag_pdf_link = soup.find("object")
        if tag_pdf_link is not None:
            pdf_link = "https://vbpl.vn/" + tag_pdf_link.get("data")
        else:
            pdf_link = None
        driver.close()
        return pdf_link

    def save_data_text(self):
        file_data_folder = self.path_save_data + "text/"
        json.dump(self.dict_data, open(file_data_folder + self.id + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    def save_data_pdf(self):
        pdf_link = self.get_pdf_link()
        if pdf_link is None:
            self.pdf = False
            return
        file_data_folder = self.path_save_data + "pdf/"
        res = None
        for _ in range(5):
            try:
                res = requests.get(pdf_link)
                break
            except:
                res = None
                continue
        if res is None:
            return
        self.pdf_dir = self.path_save_data + "pdf/" + self.id
        with open(file_data_folder + self.id + ".pdf", "wb") as f:
            f.write(res.content)
        return self.pdf_dir

    def extract_data(self):
        self.get_html()
        if self.html is None:
            print(f"Link failed: {self.url}")
            return
        else:
            self.get_attr()
            self.is_digital()
            self.is_pdf()
        if self.digital_text:
            self.get_content()
            self.create_folder_save_data()
            self.save_data_text()
        if self.content is None:
            if self.pdf:
                self.create_folder_save_data()
                self.save_data_pdf()
                self.save_data_text()
                return
        elif len(self.content) < 10:
            if self.pdf:
                self.create_folder_save_data()
                self.save_data_pdf()
                self.save_data_text()
        self.save_data_text()

    @property
    def dict_data(self):
        return {"id": self.id,
                "url": self.url,
                "attr": self.attr,
                "pdf": self.pdf,
                "digital_text": self.digital_text,
                "content": self.content,
                "dir_pdf_file": self.pdf_dir,
                "keyword": self.keywords
                }

