from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.conf import settings

from tripadvisorcom_scraper.items import HotelItem
from tripadvisorcom_scraper.spiders.crawlerhelper import get_parsed_string
from tripadvisorcom_scraper.spiders.crawlerhelper import clean_parsed_string

import pymongo
import re

class HotelsCrawler(BaseSpider):

    name = 'hotels'
    allowed_domains = ['tripadvisor.com',]

    def __init__(self):

        conn = pymongo.Connection(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

        self.start_urls = self.get_start_urls()

    def get_start_urls(self):

        for rec in self.collection.find({'item_type' : 'city'}):
            yield rec['url']

    def parse(self, response):

        url_start = 'http://www.tripadvisor.com'
        hxs = HtmlXPathSelector(response)

        # Parse the page for hotels and yield them
        # if the page is a city page

        hotel_urls = hxs.select('//a[contains(@class, "property_title")]/@href').extract()

        if hotel_urls:
            for hotel_url in hotel_urls:
                yield Request(url_start + hotel_url, self.parse)

        # Parse for the next button and yield the next city page
        # The next button is available both on the top and bottom
        # of the page. Yield any one of those
        # I chose the bottom link. Feels more... comfortable ;)

        next_page_url = clean_parsed_string(get_parsed_string(
            hxs, '//div[contains(@id, "pager_bottom")]//a[contains(@class, "guiArw sprite-pageNext  pid0")]/@href'))
        if next_page_url and len(next_page_url) > 0:
            next_page = url_start + next_page_url
            yield Request(next_page, self.parse)

        # If the page itself is a hotels page, get the details and
        # return the hotel item

        if response.url.find('/Hotel_Review') != -1:

            hi = HotelItem()

            hi['item_type'] = 'hotel'
            hi['hotel_id'] = re.search('d[0-9]+', response.url).group(0)
            hi['name'] = clean_parsed_string(get_parsed_string(
                hxs, '//h1[contains(@id, "HEADING")]/text()'))
            hi['locality'] = clean_parsed_string(get_parsed_string(
                hxs, '//div[contains(@class, "wrap infoBox")]//span[contains(@property, "v:locality")]/text()'))
            hi['region'] = clean_parsed_string(get_parsed_string(
                hxs, '//div[contains(@class, "wrap infoBox")]//span[contains(@property, "v:region")]/text()'))
            hi['postal_code'] = clean_parsed_string(get_parsed_string(
                hxs, '//div[contains(@class, "wrap infoBox")]//span[contains(@property, "v:postal-code")]/text()'))
            hi['country'] = clean_parsed_string(get_parsed_string(
                hxs, '//div[contains(@class, "wrap infoBox")]//span[contains(@property, "v:country-name")]/text()'))
            rating_string = clean_parsed_string(get_parsed_string(
                hxs, '//div[contains(@rel, "v:rating")]//img[contains(@class, "sprite-ratings")]/@alt'))
            review_count = clean_parsed_string(get_parsed_string(
                hxs, '//div[contains(@class, "rs rating")]//span[contains(@property, "v:count")]/text()'))
            # Some review counts are written '1 review' instead of just '1123'
            # So split the numerical part and convert into integer
            hi['review_count'] = int(review_count.split()[0]) if review_count else None
            hi['rating'] = float(re.search('[0-9].[0-9]', rating_string).group(0)) if rating_string else None
            hi['url'] = response.url

            print hi['name']

            yield hi

