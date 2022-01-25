
from dbModels.items import Items
from dbModels.marketableItems import MarketableItems
from dbModels.gatheringItems import GatheringItems
from dbModels.marketData import MarketData

class DBModelHandler(object):
    def __init__(self, dbHandler):
        self.items = Items(dbHandler)
        self.marketable_items = MarketableItems(dbHandler)
        self.gathering_items = GatheringItems(dbHandler)
        self.market_data = MarketData(dbHandler)
