# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

# class TechnewsPipeline:
#     def open_spider(self, spider):
#         self.file = open('technews.csv', 'w', newline='', encoding='utf-8')
#         self.writer = csv.writer(self.file)
#         self.writer.writerow(['Title', 'URL', 'Content', 'Time'])
#         self.seen_urls = set()

#     def close_spider(self, spider):
#         self.file.close()

#     def process_item(self, item, spider):
#         if item['url'] in self.seen_urls:
#             # If the URL is already seen, skip this item
#             spider.logger.info(f"Duplicate item found: {item['url']}")
#             return None
#         else:
#             # Add the URL to the seen set and write the item to CSV
#             self.seen_urls.add(item['url'])
#             self.writer.writerow([item['title'], item['url'], item['content'], item['time']])
#             return item
# pipeline.py
# pipeline.py
from openpyxl import Workbook

class TechnewsPipeline:

    def open_spider(self, spider):
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        self.sheet.title = 'Technews'
        self.sheet.append(['Title', 'URL', 'Time', 'Author', 'Content'])
        self.seen_urls = set()

    def close_spider(self, spider):
        self.workbook.save('technews.xlsx')

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

