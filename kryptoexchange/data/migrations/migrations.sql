

CREATE TABLE "movements" (
	"id"	INTEGER,
	"date"	TEXT,
	"time"	TEXT,
	"from_currency"	INTEGER,
	"from_quantity"	REAL,
	"to_currency"	INTEGER,
	"to_quantity"	REAL,
	PRIMARY KEY("id"),
	FOREIGN KEY("from_currency") REFERENCES "cryptos"("id"),
	FOREIGN KEY("to_currency") REFERENCES "cryptos"("id")
)

INSERT INTO "main"."cryptos"(
	"id","nombre_moneda") 
	VALUES 
		(
			"EUR",
			"Euro"
		), 
		(
			"ETH",
			"Ethereum"
		), 
		("LTC","Litecoin"), 
		("BNB","Binance Coin"), 
		("EOS","EOS"), 
		("TRX","TRON"),
		("BTC","Bitcoin"), 
		("XRP","Ripple"), 
		("BCH","Bitcoin Cash"), 
		("USDT","Tether"), 
		("BSV","Bitcoin SV"), 
		("ADA","Cardano");
