import scrapy
from ..items import TechnewsItem
from tqdm import tqdm
from datetime import datetime

# import scrapy
# from scrapy_selenium import SeleniumRequest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


class TechnewsSpider(scrapy.Spider):
    name = 'technews'
    
    # Keywords:
    # Intel: Intel, Intel fab, Intel foundry
    # Samsung: Samsung, Samsung fab, Samsung foundry
    # GlobalFoundries: GlobalFoundries, GlobalFoundries fab
    # SMIC: SMIC, SMIC fab
    # UMC: United Microelectronics, United Microelectronics fab
    keywords = ['intel', 'intel fab', 'intel foundry', 'samsung', 'samsung fab', 'samsung foundry', 'globalfoundries', 'globalfoundries fab', 'smic', 'smic fab', 'united microelectronics', 'united microelectronics fab']
    allowed_domains = ['technews.tw']
    # start_urls = ['https://technews.tw/category/semiconductor/']
    # start_urls = [f'https://technews.tw/google-search/?googlekeyword={keyword}']

    def __init__(self):
        self.start_page_number = 0
        self.end_page_number = 1433 #1433
        self.class_ = 'semiconductor'
    # /html/body/div[2]/div/div[1]/div/div/div/div/div/div/div[5]/div[2]/div/div/div[2]/div/div[1]
    # 
    def start_requests(self):
        for page_number in range(self.start_page_number, self.end_page_number + 1):
        # for keyword in self.keywords:
            url = f'https://technews.tw/category/{self.class_}/page/{page_number}/'
            # url = f'https://technews.tw/google-search/?googlekeyword={keyword}'
            yield scrapy.Request(url=url, callback=self.parse)
            # yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        self.crawler.stats.inc_value('scraped_count')
        
        # Check if an hour has passed since the last log
        if datetime.now().minute == 0:
            scraped_count = self.crawler.stats.get_value('scraped_count', 0)
            self.logger.info(f'Crawled {scraped_count} websites in the last hour')

        # Extract the news titles and URLs
        # /html/body/div[2]/div/section/div[1]/article[1]/div/header/table/tbody/tr[1]/td/h1/a
        # /html/body/div[2]/div/section/div[1]/article[2]/div/header/table/tbody/tr[1]/td/h1/a
        # /html/body/div[2]/div/section/div[1]/article[14]/div/header/table/tbody/tr[2]/td/span[5] time
        articles = response.xpath('/html/body/div[2]/div/section/div[1]/article')
        # print(f'Found {len(articles)} articles')
        for article in tqdm(articles):
            title = article.xpath('.//h1/a/@title').get()
            url = article.xpath('.//h1/a/@href').get()
            time = article.xpath('.//tr[2]/td/span[5]/text()').get()
            # //*[@id="post-1245757"]/div/header/table/tbody/tr[2]/td/span[5]
            
            # Print or process the extracted data
            print(f'Title: {title}, URL: {url}, Time: {time}')
            
            # Create an item and follow the URL to parse the content
            item = TechnewsItem(title=title, url=url, time=time, class_=self.class_)
            request = scrapy.Request(url=url, callback=self.parse_content)
            request.meta['item'] = item
            yield request

        # Follow pagination links
        # /html/body/div[2]/div/section/div[2]/a[5]
        # next_page = response.xpath('/html/body/div[2]/div/section/div[2]/a[5]/@href').get()
        # if next_page:
        #     yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_content(self, response):
        item = response.meta['item']
        # paragraphs = response.xpath('//div[@class="indent"]//p//text()').extract()
        # # paragraphs = paragraphs[:-1]
        # content = ' '.join(paragraphs)
        # author = /html/body/div[2]/div/div[1]/div/article/div/header/table/tbody/tr[2]/td/span[2]/a
        # author = /html/body/div[2]/div/div[1]/div/article/div/header/table/tbody/tr[2]/td/span[2]/a

        author = response.xpath('//header//table//tr[2]//td//span[2]//a/text()').get()

        paragraphs = response.xpath('//div[@class="indent"]//p')

        # 提取每個 <p> 標籤的完整內容
        content_list = [p.xpath('string(.)').get() for p in paragraphs]
        
        # 去掉最後一個 <p> 標籤的內容
        if content_list:
            content_list = content_list[:-1]
        content = '\n'.join(content_list)

        item['author'] = author
        item['content'] = content
        
        yield item

