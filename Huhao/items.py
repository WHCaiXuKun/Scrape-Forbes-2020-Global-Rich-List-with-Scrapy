# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HuhaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    rank = scrapy.Field()
    name = scrapy.Field()
    wealth = scrapy.Field()
    source = scrapy.Field()
    country = scrapy.Field()
    position = scrapy.Field()
    pass
