
class DBConfig(object):
    def __init__(self, db_handler):
        self.db = db_handler
        self.init()

    def init(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS dbConfig (
                `id` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `key` VARCHAR(255) NOT NULL,
                `value` VARCHAR(255) NOT NULL,
                `lastUpdated` DATE NOT NULL,
                CONSTRAINT `uniqueKey` UNIQUE (`key`),
                KEY idxDbConfigKey (`key`)
            )
        """, [], True)


    def add(self, key, value):
        if not self.get(key):
            self.db.execute("""
                INSERT INTO dbConfig (`key`, `value`, `lastUpdated`)
                VALUES(%s, %s, NOW())
            """, [key, value], True)

    def update(self, key, value):
        if self.get(key):
            self.db.execute("""
            UPDATE dbConfig SET `value` = %s WHERE `key` = %s
            """, [value, key], True)

    def get(self, key):
        data = self.db.execute("""
            SELECT value FROM dbConfig WHERE `key` = %s
        """, [key])
        if not data: return None
        return data[0]["value"]

    
