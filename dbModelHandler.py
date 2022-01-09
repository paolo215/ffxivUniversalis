
from dbModels.items import Items
from dbModels.marketableItems import MarketableItems

class DBModelHandler(object):
    def __init__(self, dbHandler):
        self.items = Items(dbHandler)
        self.marketable_items = MarketableItems(dbHandler)
