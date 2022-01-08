
class MarketableItems(object):
    def __init__(self, db_handler):
        self.db = db_handler
        self.init()

    def init(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS marketableItems (
                itemId INTEGER PRIMARY KEY,
                CONSTRAINT `fkMarketableItemsItemId` FOREIGN KEY (`itemId`) REFERENCES `items` (`itemId`)
            )
        """, [], True)


    def add(self, data):
        if not self.get(data["itemId"]):
            print("Inserting: " + str(data))
            self.db.execute("""
                INSERT INTO marketableItems (itemId)
                VALUES (%s)
            """, [data["itemId"]], True)

    def get_all(self):
        return self.db.execute("""
            SELECT * FROM marketableItems
        """) 
    

    def get(self, id):
        output = self.db.execute("""
            SELECT * FROM marketableItems WHERE itemId = %s
        """, [id])
        if output:
            return output[0]
        return None


