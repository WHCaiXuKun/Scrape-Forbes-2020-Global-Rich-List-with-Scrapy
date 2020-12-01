import scrapy
from ..items import *
from urllib.parse import urljoin

#scrapy crawl huhao --nolog
class HuhaoSpider(scrapy.Spider):
    name = 'huhao'
    #allowed_domains = ['huhao.com']
    start_urls = []
    for i in range(1, 16):
        url = f"https://www.phb123.com/renwu/fuhao/shishi_{i}.html"
        start_urls.append(url)

    def parse(self, response):
        rank_list = response.xpath("//table[@class='rank-table']/tbody/tr[*]/td[@class='xh']/text()").extract()
        name_list = response.xpath("//table[@class='rank-table']/tbody/tr[*]/td[2]/a[@class='cty']/p/text()").extract()
        wealth_list = response.xpath("//table[@class='rank-table']/tbody/tr[*]/td[3]/text()").extract()
        source_list = response.xpath("//table[@class='rank-table']/tbody/tr[*]/td[4]/text()").extract()
        country_list = response.xpath("//table[@class='rank-table']/tbody/tr[*]/td[5]/a/text()").extract()
        url_list = response.xpath("//table[@class='rank-table']/tbody/tr[*]/td[2]/a[@class='cty']/@href").extract()
        for rank, name, wealth, source, country, url in zip(rank_list, name_list,wealth_list,source_list,country_list, url_list):
            item = HuhaoItem()
            item["rank"] = rank
            item["name"] = name
            item["wealth"] = wealth
            item["source"] = source
            item["country"] = country
            url = "https://www.phb123.com/" + url
            yield scrapy.Request(url=url, callback=self.parse_url, meta={"huhao":item})
            #yield item
        pass

    def parse_url(self, response):
        position_list = response.xpath("//div[@class='peo-basic-m']/ul/li[8]/span/text()").getall()
        for position in position_list:
            item = response.meta.get("huhao")
            item["position"] = position
            yield item

        pass
