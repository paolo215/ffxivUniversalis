
class Items(object):
    def __init__(self, db_handler):
        self.db = db_handler
        self.init()

    def init(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                itemId INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL 
            )
        """, [], True)


    def add(self, data):
        if not self.get(data["itemId"]):
            print("Inserting: " + str(data))
            self.db.execute("""
                INSERT INTO items (itemId, name)
                VALUES (%s, %s)
            """, [data["itemId"], data["name"]], True)

    def get_all(self):
        return self.db.execute("""
            SELECT * FROM items
        """) 
    
    def get_by_name(self, name):
        output = self.db.execute("""
            SELECT * FROM items WHERE name = %s
        """, [name])
        if output:
            return output[0]
        return None
    

    def get(self, id):
        output = self.db.execute("""
            SELECT * FROM items WHERE itemId = %s
        """, [id])
        if output:
            return output[0]
        return None


