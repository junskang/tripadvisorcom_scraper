from scrapy.item import Item, Field

class CountryItem(Item):

    ''' Country and URL details '''

    item_type = Field()
    country = Field()
    geo_id = Field()
    url = Field()

class CityItem(Item):

    '''City and URL details '''

    item_type = Field()
    city = Field()
    geo_id = Field()
    url = Field()

class HotelItem(Item):

    '''Hotel and URL details '''

    item_type = Field()
    hotel_id = Field()
    name = Field()
    locality = Field()
    region = Field()
    postal_code = Field()
    country = Field()
    rating = Field()
    review_count = Field()
    url = Field()

class ReviewItem(Item):

    '''Review item with comments ratings...'''

    item_type = Field()
    hotel_id = Field()
    review_id = Field()
    review_date = Field()
    reviewer_type = Field()
    summary = Field()
    reviewer_name = Field()
    reviewer_rcount = Field()
    reviewer_locality = Field()
    content = Field()
    rating = Field()
