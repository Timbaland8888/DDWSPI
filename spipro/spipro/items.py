# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiproItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 获取当当网自营童书详情一级链接
    # go_sort_href = scrapy.Field()

    # 当当网一级父分类名称
    first_parent_name = scrapy.Field()
    #当当网童书自营一级分类名称
    first_name = scrapy.Field()

    # 当当网童书一级分类地址链接
    first_href = scrapy.Field()

    # 当当网童书一级当当自营书本详情地址链接
    first_self_href = scrapy.Field()

    #当当搜索等级一
    first_books_level_name = scrapy.Field()

    # 当当搜索等级二
    second_books_level_name = scrapy.Field()
    #二级父级分类名称
    second_parent_name = scrapy.Field()

    #当当网童书自营二级分类名称
    second_name = scrapy.Field()

    # 当当网童书二级分类地址链接
    second_href = scrapy.Field()

    # 当当网童书二级当当自营地址链接
    second_self_href = scrapy.Field()

    #当当网童书自营三级分类名称
    three_name = scrapy.Field()

    # 当当网童书三级分类地址链接
    three_href = scrapy.Field()

    # 当当网童书三级当当自营地址链接
    three_self_href_list =  scrapy.Field()

    #三级父级分类名称
    three_parent_name = scrapy.Field()

    #三级分类等级名称
    three_books_level_name = scrapy.Field()

class SprproItem(scrapy.Item):
    #封面图片
    src_img = scrapy.Field()
    #书本详情链接
    href = scrapy.Field()
    #行号
    nu = scrapy.Field()
    #书名
    book_name = scrapy.Field()
    #作者
    author_name = scrapy.Field()
    #出版社
    publishing_company_name = scrapy.Field()
    #出版时间
    publish_date = scrapy.Field()
    #ISBN
    isbn = scrapy.Field()
    #价格
    price = scrapy.Field()
    #作者简介
    author_introduce = scrapy.Field()

    #内容简介
    content_introduce = scrapy.Field()

    #编辑推荐介绍
    abstract_info = scrapy.Field()

    #编辑推荐介长图
    abstract_info_pic = scrapy.Field()

    # 产品特色长图
    feature_pic = scrapy.Field()

    # 书摘插画
    attachImage = scrapy.Field()

    #分类名称
    sort_name = scrapy.Field()












