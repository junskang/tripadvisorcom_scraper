BOT_NAME = 'tripadvisorcom_scraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['tripadvisorcom_scraper.spiders']
NEWSPIDER_MODULE = 'tripadvisorcom_scraper.spiders'
DEFAULT_ITEM_CLASS = 'tripadvisorcom_scraper.items.TripadvisorcomScraperItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'ta_new'
MONGODB_COLLECTION = 'ta_complete'

ITEM_PIPELINES = ['tripadvisorcom_scraper.pipelines.TripadvisorcomScraperPipeline',]

# Get country information from tripadvisor.com site-map.
# If site-map link changes, update the link

START_URL = 'http://www.tripadvisor.com/pages/site_map_lodging.html'
