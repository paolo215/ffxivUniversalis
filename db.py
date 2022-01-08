import os
import sys
import mysql.connector

from mysql.connector import pooling
from mysql.connector import errorcode

class DBHandler(object):
    def __init__(self, dbConfig):
        self.pool = pooling.MySQLConnectionPool(**dbConfig)

    def execute(self, statement, args=None, commit=False):
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        if args:
            cursor.execute(statement, args)
        else:
            cursor.execute(statement)

        if commit is True:
            conn.commit()
            last_row_id = cursor.lastrowid 
            self.close(cursor, conn)
            if last_row_id:
                return last_row_id
            return None
        else:
            result = cursor.fetchall()
            self.close(cursor, conn)
            return result


    def close(self, cursor, conn):
        cursor.close()
        conn.close()


