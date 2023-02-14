from crawl_data import Crawler
from objects.item_vbpl import ItemVBPL
from services.vbpl_crawl_by_search import VBPLCrawlBySearch


print("VBPL")
# Dau tu
path_save_data = "D:/New folder/New folder/"
list_key = ["Đô thị", "Giáo dục", "Tài nguyên", "Môi trường", "Thể thao", "Y tế", "Dân sự", "Văn hóa",
            "Xã hội", "Công nghệ", "Giao thông", "Vận tải"]

for key in list_key:
    print(f"Crawler: {key} ")
    search = VBPLCrawlBySearch(key, path_save_data)
    crawl_vbpl = Crawler(search, ItemVBPL, 20)
    crawl_vbpl.start()
    crawl_vbpl.join()
