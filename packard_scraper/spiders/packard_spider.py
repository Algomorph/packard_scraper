'''
Created on Mar 30, 2016
@author: Gregory Kramida

Copyrint 2016 Gregory Kramida

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import scrapy
import os.path

from packard_scraper.items import FellowProfile 

class PackardSpider(scrapy.Spider):
    '''
    Spider used to crawl through the Fellowship Directory on the Packard Foundation website
    '''
    name = "packard"
    allowed_domains = ["www.packard.org"]
    index = "https://www.packard.org"
    base_url = (index + "/what-we-fund/conservation-and-science/science/"+
                "packard-fellowships-for-science-and-engineering/fellowship"+
                "-directory")
    get_query = "/?display=grid"
    start_url = base_url + get_query

    def __init__(self,  *args, **kwargs):
        '''
        Constructor
        '''
        super(PackardSpider, self).__init__(*args, **kwargs)
    
    #program entry point
    def start_requests(self):
        '''    
        @override
        called to construct requests from start url(s)
        '''
        yield scrapy.Request(url = PackardSpider.start_url, 
                             callback=self.initiate_directory_parsing,
                             method="GET")
        
    def initiate_directory_parsing(self, response):
        profile_list_count =\
        int(response.xpath("//a[@class='page-numbers']/text()")[-1].extract())
        
        links = [str(uc_link) for uc_link in 
                 response.xpath("//div[@class='thumbnail']/a/@href").extract()]
        for url in links:
            if not self.db.contains(url):
                yield scrapy.Request(url,callback=self.parse_profile,
                                 method="GET")
                
        for i_profile_list in range(2,profile_list_count + 1):
            url = PackardSpider.base_url + "/page/"+str(i_profile_list)\
            + PackardSpider.get_query
            yield scrapy.Request(url,callback=self.parse_directory_list,
                                 method="GET")
    
    def parse_directory_list(self, response):
        links = [str(uc_link) for uc_link in 
                 response.xpath("//div[@class='thumbnail']/a/@href").extract()]
        for url in links:
            if not self.db.contains(url):
                yield scrapy.Request(url,callback=self.parse_profile,
                                 method="GET")
            else:
                print("Profile for {:s} is already in database. SKIPPING.".format(os.path.basename(url[:-1])))
                
    def parse_profile(self, response):
        profile = FellowProfile()
        profile["name"] = \
        response.xpath("//div[@class='wpb_wrapper']/h1/text()")[0].extract()
        
        profile["year"] = \
        int(response.xpath("//div[@class='wpb_wrapper']/p/strong/text()")[0].extract()[:4])
        
        profile["institution"], profile["field"] = \
        response.xpath("//div[@id='fellow-header']//div[@class='wpb_wrapper']/p/a/text()")[:2].extract() 
        
        synopsis_prelim = response.xpath("//div[@id='fellow-content']//div[@class='wpb_wrapper']/p/text()")
        if(len(synopsis_prelim) == 0):
            synopsis_prelim = response.xpath("//div[@id='fellow-content']//div[@class='wpb_wrapper']/p/span/text()")
        profile["synopsis"] = synopsis_prelim[0].extract()
        profile["url"] = response.url
        yield profile
        
    
        