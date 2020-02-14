# -*- coding: utf-8 -*-
import MySQLdb
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class YorkuPipeline(object):
    def process_item(self, item, spider):
        return item


class CoursePipeline(object):
    _query_all = "INSERT INTO `course_item` (`year`, `code`, `season`, `name`, `type`, `referer`, `url`, `status`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    _query = "INSERT INTO `course_item` (`year`, `name`, `type`, `referer`, `url`, `status`) VALUES(%s, %s, %s, %s, %s, %s)"
    _select = "SELECT * FROM `course_item` WHERE url=%s"

    def open_spider(self, spider):
        self.db = MySQLdb.connect(user='yorku', passwd='yorku123', db='yorku', host='127.0.0.1')
        self.db.autocommit(True)
        self.c = self.db.cursor()
    
    def close_spider(self, spider):
        self.db.commit()
        self.db.close()

    def process_item(self, item, spider):
        if self.c.execute(self._select, (item['url'],)):
            return item

        if 'code' in item:
            self.c.execute(self._query_all, (
                item['year'], item['code'], item['season'], item['name'], item['filetype'], item['referer'], item['url'], item['status']))
        else:
            self.c.execute(self._query, (
                'UNKNOW', item['name'], item['filetype'], item['referer'], item['url'], item['status']))
        return item
