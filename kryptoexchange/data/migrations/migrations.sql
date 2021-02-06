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