from scrapy.conf import settings

import pymongo

class TripadvisorcomScraperPipeline(object):
    
    def __init__(self):
        conn = pymongo.Connection(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item
