# -*- coding: utf-8 -*-

import time
from datetime import datetime
import logging
import re
import sys
import scrapy
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.log import configure_logging
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, url=None, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }


class MyJob:
    runningStartTs = {}
    settings = Settings({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)', 'CELERYD_CONCURRENCY': 100, 'TELNETCONSOLE_ENABLED': False})

    def itemScraped(self, item, response, spider):
        logging.info("Scrapy cost %s seconds" % (time.time() - self.runningStartTs[spider.start_urls[0]]))
        logging.info(item)
    
   
    def responseReceived(self, response, request, spider):
        #use spider.start_urls[0] not use request._url becuase scrapy remove hashtag in request._url
        if response.status == 404:
            logging.info("Crawled (404) %s" % spider.start_urls[0])

    def spiderError(self, failure, response, spider):
        logging.error('spiderError')
        logging.error(failure)

    def spiderClosed(self, spider, reason):
        logging.info("spiderClosed")

    def execute(self, runner, url):
        startTime = time.time()

        self.runningStartTs[url] = time.time()
        crawler = Crawler(QuotesSpider(), self.settings)
        crawler.signals.connect(self.itemScraped, signal=signals.item_scraped)
        crawler.signals.connect(self.spiderError, signal=signals.spider_error)
        crawler.signals.connect(self.responseReceived, signal=signals.response_received)
        crawler.signals.connect(self.spiderClosed, signal=signals.spider_closed)
    
        process.crawl(crawler, url)
            

if __name__ == "__main__":
    job = MyJob()

    configure_logging()
    process = CrawlerProcess()

    urls = ['http://quotes.toscrape.com/page/1/', 'http://quotes.toscrape.com/page/2/']
    for url in urls:
        job.execute(process, url)

    process.start()


# vim: expandtab softtabstop=4 tabstop=4 shiftwidth=4 ts=4 sw=4

