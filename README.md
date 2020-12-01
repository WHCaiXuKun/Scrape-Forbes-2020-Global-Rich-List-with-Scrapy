# Scrape-Forbes-2020-Global-Rich-List
Scrapyフレームワークで Forbes 2020 Global Rich Listでデータを集計し、データ分析を行う。

![][3]

[3]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Forbes%20Top%2010.png?raw=true

- [start.py][4]
- [spider/huhao.py][5]
- [items.py][6]
- [middlewares.py][7]
- [pipelines.py][8]
- [setting.py][9]

[4]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/start.py
[5]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Huhao/spiders/huhao.py
[6]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Huhao/items.py
[7]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Huhao/middlewares.py
[8]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Huhao/pipelines.py
[9]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Huhao/settings.py


### Scrapyとは
Scrapyは、Webサイトのクロール、 データマイニング、情報処理、 アーカイブなどの幅広い有用なアプリケーションに使用できる。構造化データを抽出するためのアプリケーションフレームワークである。スクレイピングの主な目的は、 構造化されていないソース（通常はWebページ）から構造化データを抽出すること。Scrapyはもともと Webスクレイピング 用に設計されていましたが, API( Amazon Associates Web Services のような)または汎用Webクローラーとしてデータを抽出するためにも使用できる。

### スクレピングする
```
scrapy startproject Huhao
```
scrapy startproject [filename]のコマンドでスクレピングプロジェクトを作る。
まず、Rich manのランク、名前、財産、財産源、国これら五つのデータを集計したい。これらのデータは全て[福布斯2020全球富豪榜][1]、このURLに含まれている。（目的と目的URLを立てる）
rank, name, wealth, source, countryを宣言する。

`items.py`では
```
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
```
[1]:https://www.phb123.com/renwu/fuhao/shishi.html
`items.py`はdicts として抽出されたデータを返すことができる。

続いて、/spider/`huhao.py`にスクレピングのロージックを描く。
```
#huhao.py
import scrapy
from ..items import *

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
```

yieldされたitemは`pipelines.py`で処理される。
```
#pipelines.py
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json, csv
import openpyxl


class HuhaoPipeline:
    def __init__(self):
        self.file = open("Rich_man.json", "w", encoding="utf-8")
        self.wb =openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.append(['rank', 'name', 'wealth', 'source', 'country', 'position'])
        print("file opened...")

    def process_item(self, item, spider):
        py_dict = dict(item)
        json_data = json.dumps(py_dict, ensure_ascii=False) + ",\n"
        self.file.write(json_data)
        line = [item["rank"], item["name"], item["wealth"], item["source"], item["country"], item["position"]]
        self.ws.append(line)
        print(line)
        return item

    def __del__(self):
        self.file.close()
        self.wb.save('Rich_man.xlsx')
        self.wb.close()
        print("file.closed...")
```

短期間の間に同じサーバに多数のリクエストを送信すると、サーバの負担にかけてしまうので、DOWNLOAD_DELAY = 0.5でリクエストずつ、0.5秒を遅延させる。CONCURRENT_REQUESTS = 32は３２個のスバイダに相当し、スバイダごとにリクエストを送って、効率をあげられる。データを得るためには、USER_AGENTを設定し、ブラウザのように振舞う。また、コーディングは必ずしもutf-8わけではないので、FEED_EXPORT_ENCODINGをutf-8にする。最後、必要なMIDDLEWARESを有効にする。
```
# Scrapy settings for Huhao project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Huhao'

SPIDER_MODULES = ['Huhao.spiders']
NEWSPIDER_MODULE = 'Huhao.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'Huhao.middlewares.HuhaoSpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'Huhao.middlewares.HuhaoDownloaderMiddleware': 543,
    "Huhao.middlewares.UAHuhaoDownloaderMiddleware":544
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'Huhao.pipelines.HuhaoPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
FEED_EXPORT_ENCODING = "utf-8"
```

このスクレピングのプログラムを稼働させるには、次のようにする必要がある。
```
#start.py
from scrapy.cmdline import execute

execute(("scrapy crawl huhao").split())
```
得られたデータはjson、excelの形としれ保存される。

```
{"rank": "42", "name": "约翰·马尔斯", "wealth": "289亿美元", "source": "碧桂园", "country": "美国", "position": "食品行业|继承"},
{"rank": "42", "name": "杰奎琳·马尔斯", "wealth": "289亿美元", "source": "玛氏公司", "country": "美国", "position": "食品行业|继承"},
{"rank": "40", "name": "李嘉诚", "wealth": "294亿美元", "source": "玛氏公司", "country": "中国", "position": "多元化经营|白手起家"},
{"rank": "39", "name": "何享健", "wealth": "302亿美元", "source": "长江和记实业有限公司", "country": "中国", "position": "家电|白手起家"},
{"rank": "38", "name": "谢尔登·阿德尔森", "wealth": "305亿美元", "source": "美的集团", "country": "美国", "position": "赌场|白手起家"},
{"rank": "37", "name": "孙正义", "wealth": "308亿美元", "source": "拉斯韦加斯金沙集团", "country": "日本", "position": "互联网|通信|白手起家"},
{"rank": "36", "name": "柳井正", "wealth": "311亿美元", "source": "日本软银集团", "country": "日本", "position": "时装|白手起家"}
...
```

### ヒストグラムを描く
で、獲得したデータを分析する。Top 10のRich manたちの財産のヒストグラムを描きたい。詳細は[Forbes Top 10.ipynb][2]に参照。

[2]:https://github.com/Xiong-yinghao/Scrape-Forbes-2020-Global-Rich-List-with-Scrapy/blob/main/Forbes%20Top%2010.ipynb

```
import pandas

df = pandas.read_excel("Rich_man.xlsx")
df.sort_values("rank")#ランクを小さい順に並べる。

wealth_list = []
name_list = []

for name, wealth in zip(df_["name"], df_["wealth"]):
    wealth = wealth.replace("亿美元", "")
    name_list.append(name)
    wealth_list.append(wealth)
    print(name, wealth)
    

wealth_list = list(map(int, wealth_list))　＃リストにデータはstrなので、intに変える。
wealth_list= wealth_list[:10] #財産の１０位まで取る
name_list = name_list[:10]    #名前の１０位まで取る

import matplotlib.pyplot as plt
from matplotlib import font_manager

plt.figure(figsize=(20,8), dpi=80)
a = plt.bar(range(len(name_list)), wealth_list, width=0.3)
plt.xticks(range(len(name_list)), name_list, fontproperties=my_font, rotation=45)
plt.xlabel("Name",  fontsize=20)
plt.ylabel("Wealth", fontsize=20)
plt.title("Forbes Top 10", fontsize=20)
plt.grid(linestyle=':', axis='y')
plt.savefig("./Forbes Top 10.png")
for i in a:
    h = i.get_height()
    plt.text(i.get_x() + i.get_width() / 2, h, '%d' % int(h), ha='center', va='bottom')
plt.show()
```


