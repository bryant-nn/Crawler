# /html/body/div[1]/main/div/div/div/div[2]/div[1]/div/div/div/div/ul/li[1]/div[2]/h4/a
# /html/body/div[1]/main/div/div/div/div[2]/div[1]/div/div/div/div/ul/li[2]/div[2]/h4/a

# 安裝所需套件
# pip install scrapy selenium webdriver-manager

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
from ..items import ArizonItem

# 安裝所需套件
# pip install scrapy selenium webdriver-manager

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest


class ArizonaSpider(scrapy.Spider):
    name = "arizona"
    start_urls = ['https://www.12news.com/search?q=intel']

    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 無頭模式，避免打開瀏覽器窗口
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def parse(self, response):
        print(f'URL: {response.url}')
        self.driver.get(response.url)

        # while True:
            # 模擬滾動頁面到底部
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 查找並點擊 "load more results" 按鈕
        try:
            load_more_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'load more results')]")
            load_more_button.click()
            self.driver.implicitly_wait(3)  # 等待加載新內容
        except Exception as e:
            print("No more results to load.")
            # break

        # 獲取所有加載完成後的頁面內容
        sel = Selector(text=self.driver.page_source)
        links = sel.xpath("//div[contains(@class, 'article')]//h4/a/@href").extract()

        for link in links:
            full_url = response.urljoin(link)
            yield SeleniumRequest(url=full_url, callback=self.parse_article)

        self.driver.quit()

    def parse_article(self, response):
        item = ArizonItem()
        item['url'] = response.url
        item['title'] = response.xpath("/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/h1/text()").get()
        item['author'] = response.xpath("/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/aside/div[1]/text()").get()
        item['content'] = ' '.join(response.xpath("/html/body/div[1]/main/div/div/div[1]/div[2]/div[1]/div/div[1]/div/article/div[4]//p/text()").extract())

        print(f'Title: {item["title"]}, URL: {item["url"]}, Author: {item["author"]}, Content: {item["content"]}')

        yield item

