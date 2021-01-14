from kryptoexchange import app
from flask import render_template, request, url_for, redirect
from kryptoexchange.forms import MovementForm
from datetime import datetime, date, time
import sqlite3

DBfile = app.config['DBFILE']

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
    transacciones = consulta('SELECT id , date, time, from_currency, from_quantity, to_currency, to_quantity FROM movements;')
    for transaccion in transacciones:
        preciounitario = (transaccion['from_quantity'])+(transaccion['from_quantity']) 
        print (preciounitario)
    print (transacciones)
    return render_template('listamovimientos.html', transacciones=transacciones, preciounitario=preciounitario) 

@app.route('/compra', methods=["GET", "POST"])
def nuevaCompra():
    form = MovementForm()
    if request.method == "POST":
        now = datetime.now().time()
        if form.validate():
            if 'calculadora' in request.form:
                print('¡Hola!')
                cantidadconvertida = 79
                return render_template("compra.html", cantidadconvertida=cantidadconvertida)
            else:
                consulta('INSERT INTO movements (date, time, from_currency, from_quantity, to_currency) VALUES (?, ?, ?, ?, ?);', 
                        (
                        date.today(),
                        str(now),
                        form.from_currency.data,
                        form.q1.data,
                        form.to_currency.data,
                        )
                    ) 
                return redirect(url_for('listaMovimientos')) #te devuelve a la página principal   
        else:
                return render_template("compra.html", form=form)

    return render_template("compra.html", form=form)


@app.route('/balance')
def balance():
    return render_template('balance.html')
