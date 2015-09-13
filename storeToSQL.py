import MySQLdb
import csv
from getMarket import *

class Database:

    host = 'localhost'
    user = 'root'
    password = 'victor'
    db = 'market_telescope'

    # Make sure that there is a database named 'market_telescope' on your mysql
    # other wise the initialization will fail
    def __init__(self):
        self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
        self.cursor = self.connection.cursor()
        
    def getAllSymbolsFromDB(self):
        query = """SELECT distinct(Symbol) FROM company_list;"""
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def creatCompanyIndividualTable(self, symbol):
        query = "CREATE TABLE IF NOT EXISTS %s(\
                Date DATE PRIMARY KEY,\
                Open DECIMAL(10,3), \
                High DECIMAL(10,3), \
                Low DECIMAL(10,3), \
                Close DECIMAL(10,3), \
                Volume INT, \
                AdjClose DECIMAL(10,3));" % (symbol)
        self.insert(query)
    
    # Create the table for all companies listed on NYSE and NASDAQ
    def creatCompanyListTable(self):
        query = "CREATE TABLE IF NOT EXISTS company_list(\
            Symbol VARCHAR(30) PRIMARY KEY,\
            Name VARCHAR(100),\
            LastScale DOUBLE, \
            MarketCap VARCHAR(30),\
            IPOyear INT(5),\
            Sector VARCHAR(50),\
            industry VARCHAR(100),\
            SummaryQuote VARCHAR(100),\
            Market VARCHAR(10))"
        self.insert(query)
    
        company_data = csv.reader(file('./companylist_nyse.csv'))
        company_data.next()
        count = 0
        for row in company_data:
            count += 1
            query = """INSERT IGNORE INTO company_list VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'NYSE');""" % tuple(row[0:8])
            self.insert(query)
    
        print 'Inserted NYSE companies:' + str(count)
    
        company_data = csv.reader(file('./companylist_nasdaq.csv'))
        company_data.next()
        count = 0
        for row in company_data:
            count += 1
            query = """INSERT IGNORE INTO company_list VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'NASDAQ');""" % tuple(row[0:8])
            self.insert(query)
    
        print 'Inserted NASDAQ companies:' + str(count)
    
    def query(self, query):
        cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        cursor.execute(query)

        return cursor.fetchall()
    
    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            self.connection.rollback()

    def __del__(self):
        self.connection.close()

    def fillHistoryQuoteData(self, symbol, csv_data):
        count = 0
        for row in csv_data[1:]:
            if len(row) < 7:
                continue;
            count += 1
            #print list(tuple([symbol]) + tuple(row[0:7]))
            query = """INSERT IGNORE INTO %s VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % tuple([symbol] + row[0:7])
            self.insert(query)
        print "Filled " + str(count) + " history quote data to " + symbol
        

if __name__ == "__main__":

    db = Database()

    db.creatCompanyListTable()

    all_symbols = db.getAllSymbolsFromDB()

    for symbol in all_symbols:
        #if "^" in symbol:
        #    continue
        print "Creating history quote table for company " + symbol
        db.creatCompanyIndividualTable(symbol)
    
        csv = getMarketDataToCVS(symbol)
        try:
            db.fillHistoryQuoteData(symbol, csv)
        except urllib2.HTTPError, e:
            print e

        #print csv
        time.sleep(3)

      
