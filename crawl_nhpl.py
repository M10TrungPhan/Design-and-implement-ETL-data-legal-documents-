from objects.item_nhpl import ItemNHPL
from services.nhpl_crawl_by_search import NHPLCrawlBySearch
from crawl_data import Crawler


if __name__ == "__main__":
    print("Ngân hàng pháp luật")
    path_save_data = "D:/New folder/"
    list_key = ["Đô thị", "Giáo dục", "Tài nguyên", "Môi trường", "Thể thao", "Y tế", "Dân sự", "Văn hóa",
                "Xã hội", "Công nghệ", "Giao thông", "Vận tải"]

    for key in list_key:
        print(f"Crawler: {key} ")
        search = NHPLCrawlBySearch(key, path_save_data)
        crawl_vbpl = Crawler(search, ItemNHPL, 20)
        crawl_vbpl.start()
        crawl_vbpl.join()
