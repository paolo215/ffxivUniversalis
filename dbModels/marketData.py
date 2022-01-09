
class MarketData(object):
    def __init__(self, db_handler):
        self.db = db_handler
        self.init()

    def init(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS marketData (
                itemId INTEGER PRIMARY KEY,
                isHQ BOOLEAN DEFAULT FALSE,
                quantity INTEGER NOT NULL,
                pricePerUnit INTEGER NOT NULL,
                date TIMESTAMP DEFAULT NULL,
                CONSTRAINT `fkMarketDataItemId` FOREIGN KEY (`itemId`) REFERENCES `items` (`itemId`),
                KEY idxMarketDataItemIdDate (itemId, date)
            )
        """, [], True)


    def add(self, data):
        if not self.get_by_id_and_timestamp(data["itemId"], data["timestamp"]):
            print("Inserting: " + str(data))
            self.db.execute("""
                INSERT INTO marketData (itemId, isHQ, quantity, pricePerUnit, date)
                VALUES (%s, %s, %s, %s, %s)
            """, [data["itemId"], data["isHQ"], data["quantity"], data["pricePerUnit"], data["date"]], True)

    def get_all(self):
        return self.db.execute("""
            SELECT * FROM marketData
        """) 
    

    def get_by_id_and_timestamp(self, id, ts):
        output = self.db.execute("""
            SELECT * FROM marketData WHERE itemId = %s and timestamp = %s
        """, [id, ts])
        if output:
            return output[0]
        return None

    def get(self, id):
        output = self.db.execute("""
            SELECT * FROM marketData WHERE itemId = %s
        """, [id])
        if output:
            return output[0]
        return None


