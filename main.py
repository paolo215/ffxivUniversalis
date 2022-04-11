
from db import DBHandler
from dbModelHandler import DBModelHandler
from optparse import OptionParser

import threading
import requests
import config
import sys
import os
import datetime
import time
import numpy as np
import math

THRESHOLD = 0.8

class Main(object):
    def __init__(self):
        self.db_handler = DBHandler(config.config["db"])
        self.models = DBModelHandler(self.db_handler)
        self.count = 0
        self.start = None 
        self.universalis = config.config["universalis"]


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

    def read_gathering_items(self):
        with open("GatheringItem.csv", "r") as f:
            lines = f.read().replace("\r", "").replace("\"", "").split("\n")
            lines = lines[3:]
            lines = [f for f in lines if f]
            for i in range(0, len(lines)):
                data = lines[i].split(",");
                is_available =  data[3]
                item_id = data[1]
                data = {}
                data["itemId"] = item_id
                
                if is_available == "True":
                    self.models.gathering_items.add(data)
            

    def get_marketable(self):
        url = self.universalis["base_url"] + "api/marketable"
        req = requests.get(url)
        items = req.json()
        for item in items:
            data = {}
            data["itemId"] = item
            self.models.marketable_items.add(data)


    def get_history_every(self, hours=4):
        while True:
            self.get_history()
            time.sleep(60*hours)

    def get_history(self):
        base_url = self.universalis["base_url"] + "api/history/" + self.universalis["world"] + "/"
        marketable = self.models.marketable_items.get_all()
        params = { "entries": 250, "entriesWithin": 60*60*24*7 }
        self.start = now()
        self.models.market_data.delete_after(10)
        for i in range(0, len(marketable), 50):
            current = now()
            if (current - self.start).total_seconds() > 60:
                self.reset()

            if self.count > 20:
                time.sleep(60)
                self.reset()
                

            items = [str(f["itemId"]) for f in marketable[i:i+5]]
            items_str = ",".join(items)
            url = base_url + items_str
            req = requests.get(url)
            try:
                data = req.json()
                items = data["items"]
                for item in items:
                    item_id = item["itemID"]
                    last_upload = item["lastUploadTime"]
                    entries = item["entries"]
                    for entry in entries:
                        add = {}
                        add["itemId"] = item_id
                        add["isHQ"] = entry["hq"]
                        add["pricePerUnit"] = entry["pricePerUnit"]
                        add["quantity"] = entry["quantity"]
                        add["date"] = datetime.datetime.utcfromtimestamp(entry["timestamp"])
                        if add["quantity"] != None:
                            self.models.market_data.add(add)
            except Exception as e:
                pass
            finally:
                self.count += 1 

    def reset(self):
        self.count = 0
        self.start = now()


    def get_most_expensive(self, top=25):
        items =  self.models.market_data.get_all_ids()
        output = [] 
        for item in items:
            item_id = item["itemId"]
            name = self.models.items.get(item_id)["name"]
            if not name: continue
            day1 = self.models.market_data.get_all_by_id_within(item_id, 2) 
            if not day1: continue
            ppu1 = [f["pricePerUnit"] for f in day1]
            ppu1 = self.remove_outliers(ppu1)
            if not ppu1: continue
            avg1 = np.average(ppu1)
            if not avg1: continue
            output.append([name, item_id, avg1])
        output = sorted(output, key=lambda x: x[2])[-top:]
            
        for item in output:
            print("%s (%s): %s\t%s" % (item[0], str(item[1]), item[2], self.get_universalis_link(item[1])))
        

    def get_gathering_avg(self, top=25, day=1):
        items =  self.models.gathering_items.get_all()
        output = [] 
        for item in items:
            item_id = item["itemId"]
            name = self.models.items.get(item_id)["name"]
            day1 = self.models.market_data.get_all_by_id_within(item_id, day) 
            if not day1: continue
            ppu1 = [f["pricePerUnit"] for f in day1]
            ppu1 = self.remove_outliers(ppu1)
            if not ppu1: continue
            avg1 = np.average(ppu1)
            if not avg1: continue
            output.append([name, item_id, avg1])
        output = sorted(output, key=lambda x: x[2])[-top:]
            
        for item in output:
            print("%s (%s): %s" % (item[0], str(item[1]), item[2]))


    def get_avg_diff(self, top=25, low=1, high=7):
        #data = self.models.market_data.get_all_by_id(5)
        items = self.models.gathering_items.get_all()
        cheap = []
        expensive = []
        for item in items:
            item_id = item["itemId"]
 
            day1 = self.models.market_data.get_all_by_id_within(item_id, 1) 
            day7 = self.models.market_data.get_all_by_id_within(item_id, 7) 
            if not day1 or not day7:
                continue
            ppu1 = [f["pricePerUnit"] for f in day1]
            ppu7 = [f["pricePerUnit"] for f in day7]
            ppu1 = self.remove_outliers(ppu1)
            ppu7 = self.remove_outliers(ppu7)
            avg1 = np.average(ppu1)
            avg7 = np.average(ppu7)
            abs_diff = abs(avg1 - avg7)
            if avg1 == 0 or avg7 == 0: continue
            avg = (avg1 + avg7) / 2
            res = abs_diff / avg
            name = self.models.items.get(item_id)["name"]
            if res >= THRESHOLD:
                if avg1 < avg7:
                    cheap.append([name, item_id, avg1, avg7, res])
                else:
                    expensive.append([name, item_id, avg1, avg7, res])
        cheap = list(sorted(cheap, key=lambda x: x[4]))        
        expensive = list(reversed(sorted(expensive, key=lambda x: x[2])))
        print("\n\n")
        print("Cheap by weighted avg")
        for i in cheap[-top:]:
            ##print(",".join([str(f) for f in i]))
            i = [str(f) for f in i]
            print("%s (%s)" % (i[0], i[1]))
            print("\t avg1: %s   avg7: %s  result: %s " % (i[2], i[3], i[4]))
        print("\n\n")
        print("Expensive by weighted avg")
        for i in expensive[-top:]:
            #print(",".join([str(f) for f in i]))
            print("%s (%s)" % (i[0], i[1]))
            print("\t avg1: %s   avg7: %s  result: %s " % (i[2], i[3], i[4]))
        #items = self.models.market_data.get_top_n_most_expensive_gathering(25, 1)
        #for item in items:
        #    print(item["name"], item["itemId"], item["avg"])
    

    def remove_outliers(self, arr):
        a = np.array(arr)
        a = a[ (a > np.quantile(a, 0.1)) & (a < np.quantile(a, 0.9))].tolist()
        return a


    def get_universalis_link(self, item_id):
        return self.universalis["base_url"] + "market/" + str(item_id)
    
def now():
    return datetime.datetime.now()

def main(argv):
    parser = OptionParser()
    parser.add_option("-m", "--marketHistory", dest="marketHistory", action="store_true")
    parser.add_option("-a", "--weightedAverage", dest="weightedAvg", action="store_true")
    parser.add_option("-g", "--gathering", dest="gatheringAvg", action="store_true")
    parser.add_option("-e", "--expensive", dest="mostExpensive", action="store_true")

    (options, args) = parser.parse_args(argv)
    print(options)
    print(args)

    a = Main()
    if options.marketHistory:
        a.get_history_every()
        print("\n\n")
    if options.weightedAvg:
        a.get_avg_diff()
        print("\n\n")
    elif options.gatheringAvg:
        a.get_gathering_avg(int(args[0]))
        print("\n\n")
    elif options.mostExpensive:
        a.get_most_expensive(int(args[0]))
        print("\n\n")
    
    #a6read_item_csv()
    #a.get_marketable()
    #a.get_history()
    #a.read_gathering_items()
    #a.get_avg_diff()
    #a.get_gathering_avg(10)

if __name__ == "__main__":
    main(sys.argv[1:])
