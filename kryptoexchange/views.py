from kryptoexchange import app
from flask import render_template, url_for
from kryptoexchange.forms import MovementForm
import sqlite3

DBfile = 'kryptoexchange/data/exchanges.db'

def consulta (query, params=()):
    conn = sqlite3.connect(DBfile)
    c = conn.cursor()
    
    c.execute(query, params)
    conn.commit()
    
    filas = c.fetchall()
    conn.close()

    if len(filas) == 0:
        return filas

    columnNames = []
    for columnName in c.description:
        columnNames.append(columnName[0])

    listaDeDiccionarios = []

    for fila in filas:
        d={}
        for ix, columnName in enumerate(columnNames):
            d[columnName]= fila[ix]
        listaDeDiccionarios.append(d)
    
    return listaDeDiccionarios

@app.route('/')
def listaMovimientos():
    transacciones = consulta('SELECT id , date, time, from_currency FROM movements;') 
    return render_template('listamovimientos.html', transacciones=transacciones) 


@app.route('/compra', methods=["GET", "POST"])
def nuevaCompra():
    return render_template("compra.html")


@app.route('/balance')
def balance():
    return render_template('balance.html')


