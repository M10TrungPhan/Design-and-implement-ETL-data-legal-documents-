from threading import Thread
import requests
from bs4 import BeautifulSoup


class CrawlNHPLService(Thread):

    def __init__(self):
        super(CrawlNHPLService, self).__init__()
        self.key_words = []

    def get_all_keywords(self):
        res = requests.get("https://nganhangphapluat.lawnet.vn/?kw=Doanh+nghi%E1%BB%87p")
        soup = BeautifulSoup(res.text, "lxml")
        table = soup.find("ul", attrs={"id": "list-linhvuc-cauhoi"})
        list_span = table.findAll("span")
        keywords = []
        for span in list_span:
            keywords.append(span.text)
        return keywords


