from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.conf import settings

from tripadvisorcom_scraper.items import CountryItem
from tripadvisorcom_scraper.spiders.crawlerhelper import get_parsed_string
from tripadvisorcom_scraper.spiders.crawlerhelper import clean_parsed_string

import pymongo
import re

class CountriesCrawler(BaseSpider):

    name = 'countries'
    allowed_domains = ['tripadvisor.com',]

    def __init__(self):

        conn = pymongo.Connection(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        self.start_urls = [settings['START_URL'],]

    def parse(self, response):

        url_start = 'http://www.tripadvisor.com'
        hxs = HtmlXPathSelector(response)
        country_texts = hxs.select('//h3/a/text()').extract()
        country_urls = hxs.select('//h3/a/@href').extract()
        countries = zip(country_texts, country_urls)

        for country in countries:
            print country[0]
            text, url = country
            geo_id = re.search('g[0-9]+', url).group(0)

            ci = CountryItem()
            ci['item_type'] = 'country'
            ci['country'] = text
            ci['geo_id'] = geo_id
            ci['url'] = url_start + url

            yield ci