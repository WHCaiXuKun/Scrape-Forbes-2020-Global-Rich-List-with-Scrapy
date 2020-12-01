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
