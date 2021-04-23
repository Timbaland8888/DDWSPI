import time
import urllib
import copy
from scrapy.utils.project import get_project_settings
from ..items import *
SETTINGS = get_project_settings()

class BookspiSpider(scrapy.Spider):
    name = 'bookspi'
    allowed_domains = ['category.dangdang.com']
    #图书下的童书一级分类
    # start_urls = ['http://category.dangdang.com/cp01.41.00.00.00.00.html']

    def start_requests(self):
        urls = [
            #童书链接
            'http://category.dangdang.com/cp01.41.00.00.00.00.html'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        #获取图书下当当网自营的书籍的一级分类hrf
        sort_href = response.xpath("//div[@id='go_sort']/div/div[1]/ul/li[1]/a/@href").extract_first()

        go_sort_href =  urllib.parse.urljoin(response.url,sort_href)

        yield  scrapy.Request(
            url = go_sort_href,
            callback = self.books_sort_first_1,
            dont_filter=True
        )

    def books_sort_first_1(self,response):
        """
        当当网自营链接信息
        :param response:
        :return:
        """

        #获取童书下面的当当网一级分类名称和分类地址
        item  = SpiproItem()
        level_name = SETTINGS.get('BOOKS_SETTINGS')

        # level_params = level_name.get('BOOKS_LEVEL')
        filtrate_box_path = response.xpath("//div[@id='navigation']/ul/li[@dd_name='分类']/div[2]/div[1]/div/span")
        for filtrate_span in filtrate_box_path:

            item['first_name'] = filtrate_span.xpath("./a/@title").extract_first()
            item['first_href'] = urllib.parse.urljoin(response.url,filtrate_span.xpath("./a/@href").extract_first())
            item['first_books_level_name'] = level_name['BOOKS_LEVEL']['first']
            if item["first_name"] == level_name['BOOKS_LEVEL']['first']:
                yield scrapy.Request(
                    url=item['first_href'],
                    callback=self.books_sort_first_2,
                    meta={"first_name":item['first_name']},
                    dont_filter=True

                )

    def books_sort_first_2(self, response):

        level_name = SETTINGS.get('BOOKS_SETTINGS')
        # 获取图书下当当网自营的书籍的二级分类hrf
        sort_href = response.xpath("//div[@id='go_sort']/div/div[1]/ul/li[1]/a/@href").extract_first()
        go_sort_href = urllib.parse.urljoin(response.url, sort_href)
        yield scrapy.Request(
            url=go_sort_href,
            meta={'first_name':response.meta['first_name']},
            callback=self.books_sort_first_3,
        )

    def books_sort_first_3(self, response):
        level_name = SETTINGS.get('BOOKS_SETTINGS')
        item = SpiproItem()
        #查找当前分类级别所有当当网自营分页的链接
        page_count_str = response.xpath("//*[@id='go_sort']/div/div[2]/span[2]/text()").extract_first()
        page_count = int(page_count_str.split('/')[-1])
        pg2_hrf = response.xpath("//*[@id='go_sort']//a[@class='arrow_r arrow_r_on']/@href").extract_first()
        if pg2_hrf:
            first_self_href_list = []
            first_self_href_list.append(response.url)
            for n in range(2, page_count + 1):
                # print(urllib.parse.urljoin(response.url,pg2_hrf.replace("pg2",f"pg{n}")))
                first_self_href_list.append(
                    urllib.parse.urljoin(response.url, pg2_hrf.replace("pg2", f"pg{n}")))
            item['first_self_href'] = first_self_href_list
        item["first_parent_name"] = "童书"
        item['first_href'] = response.url
        item['first_name'] = response.meta["first_name"]
        item['first_books_level_name'] = response.meta["first_name"]
        yield copy.deepcopy(item)
        #判断是否有分类标志
        list_left_flag = response.xpath("//*[@id='navigation']/ul/li[1]/div[1]/text()").extract_first()
        if list_left_flag== "分类":
            span_xpath = response.xpath("//*[@id='navigation']/ul/li[1]/div[2]/div[1]/div/span/a")
            for a_list in span_xpath:
                item["second_name"] = a_list.xpath("./@title").extract_first()
                item["second_href"] = urllib.parse.urljoin(response.url, a_list.xpath("./@href").extract_first())
                item["second_parent_name"] = item['first_name']

                if item["second_name"] == level_name['BOOKS_LEVEL']['second']:
                    yield scrapy.Request(
                        url=item['second_href'],
                        callback=self.books_sort_second_1,
                        meta={"second_name":item["second_name"]},
                        dont_filter=True

                    )
    def books_sort_second_1(self, response):
        """
        :param self:
        :param response:
        :return:
        """
        # 获取图书下当当网自营的书籍的二级分类hrf
        sort_href = response.xpath("//div[@id='go_sort']/div/div[1]/ul/li[1]/a/@href").extract_first()
        go_sort_href =  urllib.parse.urljoin(response.url,sort_href)
        yield scrapy.Request(
            url=go_sort_href,
            callback= self.books_sort_second_2,
            meta = {"second_name": response.meta["second_name"]},
        )

    def books_sort_second_2(self,response):
        item = SpiproItem()
        level_name = SETTINGS.get('BOOKS_SETTINGS')
        # 查找当前分类级别下所有当当网自营分页的链接
        page_count_str = response.xpath("//*[@id='go_sort']/div/div[2]/span[2]/text()").extract_first()
        page_count = int(page_count_str.split('/')[-1])
        pg2_hrf = response.xpath("//*[@id='go_sort']//a[@class='arrow_r arrow_r_on']/@href").extract_first()
        if pg2_hrf:
            second_self_href_list = []
            second_self_href_list.append(response.url)
            for n in range(2, page_count + 1):
                # print(urllib.parse.urljoin(response.url,pg2_hrf.replace("pg2",f"pg{n}")))
                second_self_href_list.append(
                    urllib.parse.urljoin(response.url, pg2_hrf.replace("pg2", f"pg{n}")))
        item['second_self_href'] = second_self_href_list
        item['second_name'] = response.meta['second_name']
        item['second_href'] = response.url
        item['second_parent_name'] = level_name['BOOKS_LEVEL']['first']
        item['second_books_level_name'] = item['second_parent_name']+"=>"+level_name['BOOKS_LEVEL']['second']
        yield  copy.deepcopy(item)
        # 判断是否有分类标志
        list_left_flag = response.xpath("//*[@id='navigation']/ul/li[1]/div[1]/text()").extract_first()
        if list_left_flag == "分类":
            span_xpath = response.xpath("//*[@id='navigation']/ul/li[1]/div[2]/div[1]/div/span/a")
            for a_list in span_xpath:
                item["three_name"] = a_list.xpath("./@title").extract_first()
                item["three_href"] = urllib.parse.urljoin(response.url, a_list.xpath("./@href").extract_first())
                item["three_parent_name"] = item['second_name']

                if item["three_name"] == level_name['BOOKS_LEVEL']['three']:
                    yield scrapy.Request(
                        url=item['three_href'],
                        callback=self.books_sort_three_1,
                        meta={"three_name": item["three_name"],
                              'three_books_level_name':item['second_books_level_name'],
                              "three_parent_name":item["three_parent_name"]
                              },
                        dont_filter=True

                    )


    def books_sort_three_1(self,response):
        # 获取图书下当当网自营的书籍的三级分类hrf
        sort_href = response.xpath("//div[@id='go_sort']/div/div[1]/ul/li[1]/a/@href").extract_first()
        go_sort_href = urllib.parse.urljoin(response.url, sort_href)
        yield scrapy.Request(
            url=go_sort_href,
            meta={"three_name": response.meta["three_name"],
                  'three_books_level_name':response.meta['three_books_level_name'],
                  "three_parent_name":response.meta["three_parent_name"]
                  },
            callback=self.books_sort_three_2

        )

    def books_sort_three_2(self, response):
        """

        :param self:
        :param response:
        :return:
        """
        level_name = SETTINGS.get('BOOKS_SETTINGS')
        item = SpiproItem()
        # 查找当前分类级别下所有当当网自营分页的链接
        page_count_str = response.xpath("//*[@id='go_sort']/div/div[2]/span[2]/text()").extract_first()
        page_count = int(page_count_str.split('/')[-1])
        pg2_hrf = response.xpath("//*[@id='go_sort']//a[@class='arrow_r arrow_r_on']/@href").extract_first()
        if pg2_hrf:
            three_self_href_list = []
            three_self_href_list.append(response.url)
            for n in range(2, page_count + 1):
                # print(urllib.parse.urljoin(response.url,pg2_hrf.replace("pg2",f"pg{n}")))
                three_self_href_list.append(
                    urllib.parse.urljoin(response.url, pg2_hrf.replace("pg2", f"pg{n}")))
        item['three_self_href_list'] = three_self_href_list
        item['three_books_level_name'] = response.meta['three_books_level_name']+"=>"+level_name['BOOKS_LEVEL']['three']
        item['three_name'] = response.meta["three_name"]
        item['three_href'] = response.url
        item['three_parent_name'] = response.meta["three_parent_name"]
        yield item










