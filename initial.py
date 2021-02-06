import sqlite3
from sqlite3 import Error


records_to_insert = [
    ('EUR', 'Euro'),
    ('ETH', 'Ethereum'),
    ("LTC","Litecoin"), 
	("BNB","Binance Coin"), 
    ("EOS","EOS"), 
    ("TRX","TRON"),
    ("BTC","Bitcoin"), 
    ("XRP","Ripple"), 
    ("BCH","Bitcoin Cash"), 
    ("USDT","Tether"), 
    ("BSV","Bitcoin SV"), 
    ("ADA","Cardano")
    ]
mySql_insert_query = """INSERT INTO cryptos (id, nombre_moneda) VALUES (?, ?) """

def sql_connection():
    try:
        con = sqlite3.connect('kryptoexchange/data/exchanges.db')
        return con
    except Error:
        print(Error)

def sql_table(con):
    cursorObj = con.cursor()
    cursorObj.execute("CREATE TABLE movements(id INTEGER, date TEXT, time TEXT, from_currency INTEGER, from_quantity REAL, to_currency INTEGER, to_quantity REAL, PRIMARY KEY(id), FOREIGN KEY(from_currency) REFERENCES cryptos(id), FOREIGN KEY(to_currency) REFERENCES cryptos(id))")
    con.commit()
    cursorObj.execute("CREATE TABLE cryptos(id TEXT, nombre_moneda TEXT, PRIMARY KEY(id))")
    con.commit()
    cursorObj.executemany(mySql_insert_query, records_to_insert)
    con.commit()
con = sql_connection()

sql_table(con)