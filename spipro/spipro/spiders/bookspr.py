
import re
import time
import urllib
import scrapy
import copy
import asyncio
from spipro.db.con_mysql import Con_mysql
from pyppeteer import launch
from lxml import html
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from spipro.items import SprproItem
from twisted.enterprise import adbapi


class BooksprSpider(scrapy.Spider):
    name = 'bookspr'
    allowed_domains = ['category.dangdang.com']

    urls = []
    SETTINGS = get_project_settings()
    # 获取数据库配置参数
    db_name = SETTINGS.get('DB_SETTINGS')
    db_params = db_name.get('db1')
    user_query = SETTINGS.get('BOOKS_SETTINGS')
    user_params = user_query.get('BOOKS_LEVEL')
    # 连接数据池ConnectionPool，使用pymysql，连接需要添加charset='utf8'，否则中文显示乱码
    db_pool = Con_mysql(db_params['host'],db_params['user'],db_params['password'],db_params['db'],)
    #用户设置查询的自营url
    quer_sql = None
    sort_name =None

    if user_params['first'] and user_params['second'] and user_params['three']:
        quer_sql = f"""SELECT self_href from book_self_info WHERE books_level_name ='{user_params['first']}=>{user_params['second']}=>{user_params['three']}'  """
        sort_name = user_params['first']+'=>'+user_params['second']+'=>'+user_params['three']
    else:
        if user_params['first'] and user_params['second'] :
            quer_sql = f"""SELECT self_href from book_self_info WHERE books_level_name ='{user_params['first']}=>{user_params['second']}'  """
            sort_name = user_params['first'] + '=>' + user_params['second']
        else:
            quer_sql = f"""SELECT self_href from book_self_info WHERE books_level_name ='{user_params['first']}'  """
            sort_name = user_params['first']
    print(quer_sql)
    result_url = db_pool.query(quer_sql)
    print(result_url)
    for self_hrf in result_url:
        # print(self_hrf[0])
        urls.append(self_hrf[0])
    custom_settings = {
        "ITEM_PIPELINES": {"spipro.pipelines.SprproPipeline": 301},
    }
    def start_requests(self):

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 获取图书下当当网自营的书籍的一级分类hrf
        item = SprproItem()
        item['sort_name'] = self.sort_name
        href_xpath = response.xpath("//*[@id='search_nature_rg']/ul/li/a")
        for nu, li in enumerate(href_xpath):
            item['href'] = li.xpath("./@href").extract_first()
            item['nu'] = nu
            item['src_img'] = li.xpath("./img/@src").extract_first()
            if re.match(r'http', item['src_img']) is None:
                item['src_img'] = li.xpath("./img/@data-original").extract_first()
            yield scrapy.Request(
                url=item['href'],
                callback=self.books_detail,
                meta={"item":copy.deepcopy(item)},
                dont_filter=True
            )


    def books_detail(self,respond):

        item = respond.meta['item']
        item['book_name'] = respond.xpath("//*[@id='product_info']/div/h1/@title").extract_first()
        item['author_name'] = respond.xpath("//*[@id='product_info']//a[@dd_name='作者']/text()").extract_first()
        item['publishing_company_name'] = respond.xpath(
            "//*[@id='product_info']//a[@dd_name='出版社']/text()").extract_first()
        item['publish_date'] = respond.xpath("//*[@id='product_info']/div[2]/span[3]/text()").extract_first()
        if item['publish_date']:
            item['publish_date'] = item['publish_date'].split('出版时间:')[-1].split('\xa0')[0]
        li_list = respond.xpath("//*[@id='detail_describe']/ul/li//text()").extract()
        for li in li_list:
            if '国际标准书号ISBN：' in li:
                item['isbn'] = li.split('国际标准书号ISBN：')[-1]
        if respond.xpath("//*[@id='dd-price']/text()").extract():
            item['price'] = ''.join(respond.xpath("//*[@id='dd-price']/text()").extract()[-1]).rstrip()

        yield scrapy.Request(
            url=item['href'],
            callback=self.product_tab,
            meta={"item": copy.deepcopy(item)},
            dont_filter=True
        )

    def product_tab(self,respond):
        item = respond.meta['item']
        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument("--headless")
        browser = webdriver.Chrome(options=chrome_opts)
        browser.get(respond.url)
        out_html = browser.page_source
        tree = html.fromstring(out_html)
        browser.close()
        """
        书名作者简介
        """
        pre = re.compile('>(.*)<')
        author_introduce_str = ''.join(
            tree.xpath('//*[@id="detail"]/div[@id="authorIntroduction"]/div[@class="descrip"]//text()'))

        retouve_str = ''.join(pre.findall(author_introduce_str))
        if retouve_str:
            author_introduce = retouve_str.strip()
        else:
            author_introduce = author_introduce_str.strip()
        item['author_introduce'] = author_introduce

        """
        获取书名内容简介introduce
        """
        # p标签下面的内容
        introduce_str = ''.join(tree.xpath('//*[@id="detail"]/div[@id="content"]/div[@class="descrip"]//text()'))

        pre = re.compile('>(.*)<')
        retouve_str = ''.join(pre.findall(introduce_str))

        if retouve_str:
            content_introduce = retouve_str.strip()
        else:
            content_introduce = introduce_str.strip()
        # print('内容简介:', content_introduce)
        item['content_introduce'] = content_introduce
        """
        编辑推荐介绍 和 编辑推荐介长图
        """
        abstract_info_span = tree.xpath('//*[@id="detail"]/div[@id="abstract"]/div[@class="descrip"]//text()')
        abstract_info = ''.join(abstract_info_span).strip()
        # print('编辑推荐：', abstract_info)
        item['abstract_info'] = abstract_info
        abstract_info_pic = ''.join(tree.xpath('//*[@id="detail"]/div[@id="abstract"]/div[@class="descrip"]//*/@src'))
        # print('编辑推荐长图：', abstract_info_pic)
        item['abstract_info_pic'] = abstract_info_pic

        """
        产品特色长图 
        """
        feature_pic = ''.join(tree.xpath('//*[@id="detail"]/div[@id="feature"]/div[@class="descrip"]//*/@src'))
        if not feature_pic:
            feature_pic = ''.join(
                tree.xpath('//*[@id="detail"]/div[@id="feature"]/div[@class="descrip"]//*/@data-original'))
        # print('产品特色长图：', feature_pic)
        item['feature_pic'] = feature_pic

        """
          书摘插画
          """
        attachImage = ''.join(
            tree.xpath('//*[@id="detail"]/div[@id="attachImage"]/div[@class="descrip"]//*/img/@data-original'))
        if not attachImage:
            attachImage = ''.join(tree.xpath(
                '//*[@id="detail"]/div[@id="attachImage"]/div[@class="descrip"]//*/img/@src'))

        # print('书摘插画：', attachImage)
        item['attachImage'] = attachImage
        yield item



















