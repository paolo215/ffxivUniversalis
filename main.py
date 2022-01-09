
from db import DBHandler
from dbModelHandler import DBModelHandler

import requests
import config
import sys
import os

class Main(object):
    def __init__(self):
        self.db_handler = DBHandler(config.config["db"])
        self.models = DBModelHandler(self.db_handler)
        


    def read_item_csv(self):
        with open("Item.csv", "r") as f:
            lines = f.read().replace("\r", "").replace("\"", "").split("\n")
            lines = lines[5:]
            lines = [f for f in lines if f]
            for i in range(0, len(lines)):
                data = lines[i].split(",");
                is_untradable = data[22]
                key = data[0]
                name = data[9] 
                item = {}
                item["itemId"] = int(key)
                item["name"] = name
                self.models.items.add(item)


    def get_marketable(self):
        url = config.config["universalis"]["base_url"] + "api/marketable"
        req = requests.get(url)
        items = req.json()
        for item in items:
            data = {}
            data["itemId"] = item
            self.models.marketable_items.add(data)


def main(argv):
    a = Main()
    a.read_item_csv()
    a.get_marketable()

if __name__ == "__main__":
    main(sys.argv[1:])
