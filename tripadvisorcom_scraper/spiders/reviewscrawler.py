from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.conf import settings

from tripadvisorcom_scraper.items import ReviewItem
from tripadvisorcom_scraper.spiders.crawlerhelper import get_parsed_string
from tripadvisorcom_scraper.spiders.crawlerhelper import clean_parsed_string
from tripadvisorcom_scraper.spiders.crawlerhelper import get_parsed_review_element

import pymongo
import re
import time

class ReviewsCrawler(BaseSpider):

    name = 'reviews'
    allowed_domains = ['tripadvisor.com',]

    def __init__(self):

        conn = pymongo.Connection(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

        self.start_urls = self.get_start_urls()

    def get_start_urls(self):

        # Replace {'item_type' : 'hotels'}
        # with
        # {'item_type' : 'hotels', 'locality' : '<locality_name>'}
        # to crawl for hotels only in that locality
        #
        # Eg.,
        # {'item_type' : 'hotels', 'locality' : 'New York City'}
        # will crawl for hotels only in New York City

        for rec in self.collection.find({'item_type' : 'hotel'}):
            yield rec['url']

    def parse(self, response):

        url_start = 'http://www.tripadvisor.com'
        hxs = HtmlXPathSelector(response)

        # The default hotels page contains the reviews
        # but the reviews are shrunk and need to click
        # 'more' to view the complete content. An alternate
        # way is to click one of the reviews in the page

        review_url = clean_parsed_string(get_parsed_string(
            hxs, '//div[contains(@class, "basic_review first")]//a/@href'))

        if review_url:
            yield Request(url_start + review_url, self.parse)

        # If the page is not a basic review page, we can proceed with
        # parsing the reviews

        else:
            raw_reviews = hxs.select('//div[contains(@class, "review extended")]')
            for raw_review in raw_reviews:
                ri = ReviewItem()
                ri['item_type'] = 'review'
                ri['hotel_id'] = re.search('d[0-9]+', response.url).group(0)
                ri['review_id'] = clean_parsed_string(get_parsed_review_element(
                    raw_review, '@id'))
                rdate_text = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//span[contains(@class, "ratingDate")]/text()'))
                rdate_text = rdate_text.split('Reviewed')[1].strip() if rdate_text else None
                rdate = time.strptime(rdate_text, '%B %d, %Y') if rdate_text else None
                ri['review_date'] = time.strftime('%Y-%m-%d', rdate) if rdate else None
                ri['reviewer_type'] = None # TODO: Try to find the info and insert here
                ri['summary'] = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//div[contains(@class, "quote")]/text()'))
                ri['reviewer_name'] = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//div[contains(@class, "username mo")]/span/text()'))
                reviewer_rcount = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//div[contains(@class, "totalReviewBadge")]//span[contains(@class, "badgeText")]/text()'))
                ri['reviewer_rcount'] = int(reviewer_rcount.split()[0]) if reviewer_rcount else None
                reviewer_locality = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//div[contains(@class, "member_info")]//div[contains(@class, "location")]/text()'))
                ri['reviewer_locality'] = reviewer_locality.title() if reviewer_locality else None
                ri['content'] = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//div[contains(@class, "entry")]//p'))
                rating_text = clean_parsed_string(get_parsed_review_element(
                    raw_review, 'div//div[contains(@class, "rating reviewItemInline")]//img/@alt'))
                ri['rating'] = int(rating_text.split()[0]) if rating_text else None
                ri['recommendations'] = raw_review.select('div//li[contains(@class, "recommend-answer")]').extract()

                print '%s:%s:%s' % (ri['review_id'], ri['reviewer_name'], ri['review_date'])

                yield ri

        # Find the next page link if available and yield it

        next_page_url = clean_parsed_string(get_parsed_string(
            hxs, '//a[contains(@class, "guiArw sprite-pageNext")]/@href'))
        if next_page_url and len(next_page_url) > 0:
            next_page = url_start + next_page_url
            yield Request(next_page, self.parse)