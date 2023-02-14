import logging
import os
import time
import random

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import ProxyType, Proxy

from config.config import Config


def setup_logging():
    config = Config()
    os.makedirs(config.logging_folder, exist_ok=True)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(name)s | [%(levelname)s] | %(message)s",
                        handlers=[logging.FileHandler(os.path.join(config.logging_folder, config.logging_name),
                                                      encoding="utf8"),
                                  logging.StreamHandler()])


def setup_selenium_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.headless = True
    ser = Service("chromedriver_win32/chromedriver.exe")
    prox = "localhost:8080"
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = prox
    capabilities = webdriver.DesiredCapabilities.CHROME
    proxy.add_to_capabilities(capabilities)
    driver = webdriver.Chrome(service=ser,
                              options=chrome_options,
                              desired_capabilities=capabilities)
    return driver


def setup_selenium_firefox():
    ser = Service("D:/trungphan/crawl_shoppe/chromedriver_win32/geckodriver.exe")
    firefox_options = FirefoxOptions()
    firefox_options.set_preference('devtools.jsonview.enabled', False)
    firefox_options.set_preference('dom.webnotifications.enabled', False)
    firefox_options.add_argument("--test-type")
    firefox_options.add_argument('--ignore-certificate-errors')
    firefox_options.add_argument('--disable-extensions')
    firefox_options.add_argument('disable-infobars')
    firefox_options.add_argument("--incognito")
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(service=ser, options=firefox_options)
    return driver




def change_vpn():
    time.sleep(10)
    list_country = ["Viet nam", "South Korea", "Malaysia", "Japan",
                    "Taiwan", "Hong Kong", "Indonesia", "Singapore"]
    country = random.choice(list_country)
    os.system("""nordvpn.lnk -c -g "{}" """.format(country))
    print(f"CONNECT VPN IN {country}")
    time.sleep(20)

setup_logging()
# log = logging.getLogger(__name__)
