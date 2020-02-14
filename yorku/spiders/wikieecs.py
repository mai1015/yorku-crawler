# -*- coding: utf-8 -*-
import scrapy
import re
import os
from yorku.items import CourseItem
from scrapy.utils.python import to_native_str

class WikieecsSpider(scrapy.Spider):
    http_user = 'user'
    http_pass = 'pass'

    base_path = './data'

    name = 'wikieecs'
    allowed_domains = ['wiki.eecs.yorku.ca', 'www.eecs.yorku.ca']
    start_urls = ['https://wiki.eecs.yorku.ca/course_archive/',
                  'https://www.eecs.yorku.ca/course_archive/']
    # start_urls = [
    #     'https://www.eecs.yorku.ca/course_archive/2017-18/W/3101Z/']
    #   'https://wiki.eecs.yorku.ca/course_archive/2018-19/F/2031E/lab:start']
    
    ext = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt', '.v', '.c', '.tar', '.tar.gz', '.zip']
    ignore = ['/teaching/', '/research/', '/lab/']

    download = ['2015-16', '2016-17', '2017-18', '2018-19', '2019-20']

    m = re.compile(r'(\d{4}-\d{2})\/([FWS])\/(\d{4})')
    
    def getItem(self, refer, url, status):
        match = self.m.search(refer)
        filename = url.split("/")[-1]
        filename = filename.split("?")[0]
        name = filename.split(".", 2)
        filetype = "UNKNOW"
        if len(name) > 1:
            filetype = name[1]

        if match:
            return CourseItem(name=filename, filetype=filetype, referer=refer, url=url, status=status, code=match.group(3), season=match.group(2), year=match.group(1))
        else:
            return CourseItem(name=filename, filetype=filetype, referer=refer, url=url, status=status)

    def getCat(self, response):
        # match = re.match(
        #    r'.*\/(\d{4}-\d{2})\/([FWS])\/(\d{4})\w*\/.*', response.url)
        match = self.m.search(response.url)
        if match:
            return {'year': match.group(1),
                    's': match.group(2),
                    'code': match.group(3)}
        return None

    def parse(self, response):
        if any(ext in response.url for ext in self.ignore):
            return

        if 'Content-Type' not in response.headers or b'text/html' not in response.headers['Content-Type']:
            # self.save_file(response)
            yield self.getItem(response.url, response.url, 3)
            return

        meta = self.getCat(response)
        self.logger.info('Info: %s', meta)
        for url in response.css('a::attr(href)'):
            link = url.extract()
            if re.search(r'\/teaching\/', link):
                continue

            if link.endswith(tuple(self.ext)):
                # yield self.getItem(response.url, link, 1)
                if any(path in response.url for path in self.download):
                    yield self.getItem(response.url, link, 0)
                    if meta == None:
                        yield response.follow(link, self.save_file)
                    else:
                        yield response.follow(link, self.save_file, meta=meta)
                else:
                    yield self.getItem(response.url, link, 1)
            else:
                yield response.follow(link, self.parse)
                pass

    def save_file(self, response):
        filename = response.url.split("/")[-1]
        path = ""
        if 'code' in response.meta:
            path = os.path.join(self.base_path, response.meta['year'], response.meta['s'], response.meta['code'])
        else:
            path = os.path.join(self.base_path, 'UNKNOWN')
        self.logger.info('Path: %s', path)
        
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, filename), 'wb') as f:
            f.write(response.body)
        self.logger.info('Save file %s', filename)
