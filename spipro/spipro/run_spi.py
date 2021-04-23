"""
Author：
Date：
Fuction：

"""
import os
import sys
import time

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


from scrapy.cmdline import execute

if __name__ == '__main__':

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # 执行爬虫程序
    # execute(['scrapy', 'crawl', 'bookspi'])
    # execute(['scrapy', 'crawl', 'bookspr'])
    process = CrawlerProcess(get_project_settings())
    process.crawl('bookspi')
    process.start()













