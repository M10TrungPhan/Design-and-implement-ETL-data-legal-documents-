import os
import re
import json
import hashlib

import requests
from bs4 import BeautifulSoup

from objects.item import Item


class ItemNHPL(Item):

    def __init__(self, url: str, keyword: str, path_save_data: str):
        super(ItemNHPL, self).__init__(url)
        self.url = url
        self.keyword = keyword
        self.html = None
        self.data = None
        self.path_save_data = path_save_data
        self.vbpl = []

    def get_html(self, url):
        res = None
        for _ in range(5):
            try:
                res = requests.get(url)
                break
            except:
                res = None
                continue
        if res is None:
            soup = None
            return soup
        soup = BeautifulSoup(res.text, "lxml")
        return soup

    def get_tag_ques(self):
        box = self.html.find("div", {"id": "tra-loi"})
        box = box.find("span")
        ques_tag = box.findAll("h2")
        list_tag_data = []
        if len(ques_tag):
            for q in ques_tag:
                que = q
                list_tag_ans = []
                while True:
                    tag_p = que.find_next_sibling()
                    if tag_p is None:
                        break
                    if tag_p.name == "p":
                        list_tag_ans.append(tag_p)
                        que = tag_p
                    else:
                        break
                list_tag_data.append({"tag_q": q, "tag_ans": list_tag_ans})
        else:
            q = self.html.find("h1")
            list_tag_ans = box.findAll("p")
            list_tag_data.append({"tag_q": q, "tag_ans": list_tag_ans})
        return list_tag_data

    @staticmethod
    def get_atrribute_ques(tag_ques):
        # GET TEXT
        text = tag_ques.text
        # CHECK BOLD
        if tag_ques.find("strong") is not None:
            is_bold = True
        else:
            is_bold = False
        return {"text": text, "is_bold": is_bold}

    @staticmethod
    def get_atrribute_ans(list_tag_ans):
        list_ans = []
        for tag in list_tag_ans:
            # GET TEXT
            text = tag.text
            if re.search("Trân trọng!", text) is not None:
                continue
            # CHECK BOLD
            if tag.find("strong") is not None:
                is_bold = True
            else:
                is_bold = False
            # CHECK URL
            tag_url = tag.find("a")
            if tag_url is not None:
                url = tag_url.get("href")
            else:
                url = ""
            list_ans.append({"text": text, "is_bold": is_bold, "url": url})
        return list_ans

    def get_text_data(self):
        list_tag_data = self.get_tag_ques()
        list_data = []
        for each_ques in list_tag_data:
            tag_ques = each_ques["tag_q"]
            ques_data = self.get_atrribute_ques(tag_ques)
            tag_ans = each_ques["tag_ans"]
            ans_data = self.get_atrribute_ans(tag_ans)
            list_data.append({"question": ques_data, "answer": ans_data})
        self.data = list_data
        return self.data

    def extract_data(self):
        self.html = self.get_html(self.url)
        if self.html is None:
            print(f"Link failed:{self.url}")
        else:
            self.get_text_data()
            self.get_vbpl()
            self.save_data_text()
            # print(f"save {self.url}")

#######################################################################

    def get_link_vpbl(self):
        list_link = []
        box_contain_all_link = self.html.find("div", class_="lv-content-cancu-phaply")
        if box_contain_all_link is None:
            return list_link
        list_box_each_link = box_contain_all_link.findAll("span", class_="vp-title")
        if len(list_box_each_link) is None:
            return list_link
        for each in list_box_each_link:
            list_link.append(each.find("a").get("href"))
        return list_link

    def get_vbpl(self):
        list_link_vbpl = self.get_link_vpbl()
        for each in list_link_vbpl:
            data = self.extract_vbpl(each)
            if data is None:
                continue
            name = "vpbl_attached/" + data["_id"] + ".json"
            if name in self.vbpl:
                continue
            self.vbpl.append(name)
            self.save_vpbl(data)

    def extract_vbpl(self, url):
        soup = self.get_html(url)
        if soup is None:
            return None
        tag_data = soup.find("table", attrs={"border": "0"})
        if tag_data is None:
            return
        text = tag_data.get_text(" ", strip=True).replace("\r", " ")\
                   .replace("\n", " ").replace("  ", " ").replace(" ", " ") + "\n"
        while True:
            tag_data = tag_data.find_next_sibling()
            if tag_data is None:
                break
            text = text + tag_data.get_text(" ", strip=True).replace("\r", " ")\
                .replace("\n", " ").replace("  ", " ").replace(" ", " ") + "\n"
        title = soup.find("h1").get_text("", strip=True)
        id_data = hashlib.md5(text.encode("utf-8")).hexdigest()
        data = {"_id": id_data, "url": url, "title": title, "text": text}
        return data

    def save_vpbl(self, data):
        file_data_folder = self.path_save_data + "vpbl_attached/"
        json.dump(data, open(file_data_folder + data["_id"] + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    @property
    def dict_data(self):
        return {"id": self.id,
                "url": self.url,
                "data": self.data,
                "keyword": self.keyword,
                "vbpl_attached": self.vbpl}

    def save_data_text(self):
        file_data_folder = self.path_save_data + "text/"
        json.dump(self.dict_data, open(file_data_folder + self.id + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)
