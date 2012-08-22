from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.conf import settings

from tripadvisorcom_scraper.items import CityItem
from tripadvisorcom_scraper.spiders.crawlerhelper import get_parsed_string
from tripadvisorcom_scraper.spiders.crawlerhelper import clean_parsed_string

import pymongo
import re

class CitiesCrawler(BaseSpider):

    name = 'cities'
    allowed_domains = ['tripadvisor.com',]

    def __init__(self):

        conn = pymongo.Connection(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

        self.start_urls = self.get_start_urls()

    def get_start_urls(self):

        for rec in self.collection.find({'item_type' : 'country'}):
            yield rec['url']


    def parse(self, response):

        url_start = 'http://www.tripadvisor.com'
        hxs = HtmlXPathSelector(response)

        # The locations may or may not contain sub-locations

        sub_urls = hxs.select('//div[contains(@class, "rolluptopdestlink")]/a/@href').extract()

        # If the page contain sub-locations request all the
        # sub-locations and yield the next page if available

        if sub_urls:
            for sub_url in sub_urls:
                city_url = url_start + sub_url
                yield Request(city_url, self.parse)

            # Now comes the next-page part
            next_page_url = clean_parsed_string(get_parsed_string(
                hxs, '//a[contains(@class, "guiArw sprite-pageNext")]/@href'))
            if next_page_url and len(next_page_url) > 0:
                next_page = url_start + next_page_url
                yield Request(next_page, self.parse)

        # If no sub-locations are present, return the CityItem
        else:
            url = response.url
            city = clean_parsed_string(get_parsed_string(
                hxs, '//h1[contains(@class, "header")]/text()'))
            geo_id = re.search('g[0-9]+', url).group(0)

            city = city.split('Hotels')[0].strip() if city else None

            print city

            ci = CityItem()
            ci['item_type'] = 'city'
            ci['city'] = city
            ci['geo_id'] = geo_id
            ci['url'] = url

            yield ci

