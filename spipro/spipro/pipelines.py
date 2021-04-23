# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import scrapy
from itemadapter import ItemAdapter
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
SETTINGS = get_project_settings()

class SpiproPipeline:
    """
       异步插入到数据库
    """

    def __init__(self, db_pool):

        self.db_pool = db_pool

    @classmethod
    def from_settings(cls,settings):
        """
        建立数据库的连接
        :param settings:
        :return: db_pool数据库连接池
        """
        # 获取数据库配置参数
        db_name = SETTINGS.get('DB_SETTINGS')
        db_params = db_name.get('db1')
        # 连接数据池ConnectionPool，使用pymysql，连接需要添加charset='utf8'，否则中文显示乱码
        db_pool = adbapi.ConnectionPool('pymysql', **db_params, charset='utf8')

        return cls(db_pool)

    def process_item(self, item, spider):
        """
         使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
         :param item:
         :param spider:
         :return:
         """
        if spider.name == "bookspi":
            self.db_pool.runInteraction(self.do_insert, item)

    @staticmethod
    def do_insert(cursor, item):

        first_name = item.get('first_name')
        first_href = item.get('first_href')
        first_parent_name = item.get('first_parent_name')
        first_books_level_name = item.get('first_books_level_name')
        first_self_href = item.get('first_self_href')
        second_name = item.get('second_name')
        second_href = item.get('second_href')
        second_self_href = item.get('second_self_href')
        second_parent_name = item.get('second_parent_name')
        three_name = item.get('three_name')
        three_href = item.get('three_href')
        three_parent_name = item.get('three_parent_name')
        second_books_level_name = item.get('second_books_level_name')
        three_self_href_list = item.get('three_self_href_list')
        three_books_level_name = item.get('three_books_level_name')

        # 插入first_sort表
        if first_name or first_href:

            insert_sql = f""" REPLACE INTO `first_sort` VALUES (REPLACE(UUID(), '-', ''),  '{first_name}','{first_parent_name}','{first_href}',now())"""

            try:
                cursor.execute(insert_sql)
                logging.info("first_sort表数据插入成功 => ")
                if first_self_href:
                    for self_href in  first_self_href:
                        insert_book_self_sql = f""" REPLACE INTO `book_self_info` VALUES (REPLACE(UUID(), '-', ''),  '{first_books_level_name}','{self_href}',now())"""
                        cursor.execute(insert_book_self_sql)
                logging.info("book_self_info表数据插入成功 => ")
            except Exception as e:
                logging.error("first_sort or book_self_info表执行sql异常 => " + str(e))

            # 插入second_sort表
        if second_name or second_href:

            insert_sql = f""" REPLACE INTO `second_sort` VALUES (REPLACE(UUID(), '-', ''),  '{second_name}','{second_href}','{second_parent_name}',now())"""
            try:
                cursor.execute(insert_sql)
                logging.info("second_sort表数据插入成功 => ")
                if second_self_href:
                    for self_href in second_self_href:
                        insert_book_self_sql = f""" REPLACE INTO `book_self_info` VALUES (REPLACE(UUID(), '-', ''),  '{second_books_level_name}','{self_href}',now())"""
                        cursor.execute(insert_book_self_sql)
                logging.info("book_self_info表数据插入成功 => ")
            except Exception as e:
                logging.error("second_sort表执行sql异常 => " + str(e))

            # 插入three_sort表
        if three_name or three_href:

            insert_sql = f""" REPLACE INTO `three_sort` VALUES (REPLACE(UUID(), '-', ''),  '{three_name}','{three_href}','{three_parent_name}',now())"""
            try:
                cursor.execute(insert_sql)
                logging.info("three_sort表数据插入成功 => ")
                if three_self_href_list:
                    for self_href in three_self_href_list:
                        insert_book_self_sql = f""" REPLACE INTO `book_self_info` VALUES (REPLACE(UUID(), '-', ''),  '{three_books_level_name}','{self_href}',now())"""
                        # print(insert_book_self_sql)
                        cursor.execute(insert_book_self_sql)
                logging.info("book_self_info表数据插入成功 => ")
            except Exception as e:
                logging.error("three_sort表执行sql异常 => " + str(e))

    def close_spider(self, spider):
        '''
        1、关闭数据库连接
        :param spider:
        :return:
        '''
        self.db_pool.close()


class SprproPipeline:
    """
       异步插入到数据库
    """

    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        """
        建立数据库的连接
        :param settings:
        :return: db_pool数据库连接池
        """
        # 获取数据库配置参数
        db_name = SETTINGS.get('DB_SETTINGS')
        db_params = db_name.get('db1')
        # 连接数据池ConnectionPool，使用pymysql，连接需要添加charset='utf8'，否则中文显示乱码
        db_pool = adbapi.ConnectionPool('pymysql', **db_params, charset='utf8')

        return cls(db_pool)

    def process_item(self, item, spider):
        """
         :param item:
         :param spider:
         :return:
         """
        if spider.name == "bookspr":
            self.db_pool.runInteraction(self.do_insert, item)

    @staticmethod
    def do_insert(cursor, item):
        href = item.get('href')
        src_img = item.get('src_img')
        book_name = item.get('book_name')
        author_name = item.get('author_name')
        publishing_company_name = item.get('publishing_company_name')
        publish_date = item.get('publish_date')
        price = item.get('price')
        isbn = item.get('isbn')
        author_introduce = item.get('author_introduce')
        content_introduce = item.get('content_introduce')
        abstract_info = item.get('abstract_info')
        abstract_info_pic = item.get('abstract_info_pic')
        feature_pic = item.get('feature_pic')
        attachImage = item.get('attachImage')
        sort_name = item.get('sort_name')
        # 插入t_book表
        """
            提取字段sql语句到mysql数据库
        """
        tbook_sql = f""" REPLACE INTO `t_book` 
                VALUES (REPLACE(UUID(), '-', ''),'{sort_name}','{book_name}','{author_name}','{publishing_company_name}','{isbn}','{publish_date}','{content_introduce}','{price}','{author_introduce}','{abstract_info}','{abstract_info_pic}','{feature_pic}','{attachImage}','{src_img}','{href}',now())

        """
        try:
            cursor.execute(tbook_sql)
            logging.info("t_book表数据插入成功 => ")
        except Exception as e:
            logging.error("t_book表执行sql异常 => " + str(e))


    def close_spider(self, spider):
        '''
        1、关闭数据库连接
        :param spider:
        :return:
        '''
        self.db_pool.close()
