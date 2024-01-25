import mysql.connector
import threading
import time

class SQLConnector:
    def __init__(self,
                 host: str,
                 user: str,
                 password: str,
                 database: str,
                 autocommit=True):
        
        print(host)
        self.connection = mysql.connector.connect(user=user,
                                                  password=password,
                                                  host=host,
                                                  database=database)
        self.cursor = self.connection.cursor()

    def destroy(self):
        self.connection.close()
