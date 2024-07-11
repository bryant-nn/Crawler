# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook
import os
class ArizonPipeline:
    def open_spider(self, spider):
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = 'Arizona'
        self.sheet.append(['Title', 'URL', 'Time', 'Author', 'Content'])

        if os.path.exists('seen_urls.txt'):
            with open('seen_urls.txt', 'r') as file:
                self.seen_urls = set(file.read().splitlines())
        else:
            self.seen_urls = set()

        # self.seen_urls = set()

    def close_spider(self, spider):
        self.workbook.save('arizona.xlsx')
        with open('seen_urls.txt', 'w') as file:
            for url in self.seen_urls:
                file.write(url + '\n')

    def process_item(self, item, spider):
        if item['url'] in self.seen_urls:
            # If the URL is already seen, skip this item
            spider.logger.info(f"Duplicate item found: {item['url']}")
            return None
        else:
            # Add the URL to the seen set and write the item to XLSX
            self.seen_urls.add(item['url'])
            self.sheet.append([item['title'], item['url'], item['time'], item['author'], item['content']])
            return item
