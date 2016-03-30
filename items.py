# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class FellowProfile(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    year = scrapy.Field(serializer=int)
    institution = scrapy.Field()
    field = scrapy.Field()
    synopsis = scrapy.Field()
    url = scrapy.Field(serializer=str)
    
    
    
