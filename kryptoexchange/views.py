from kryptoexchange import app
from flask import render_template, flash, request, url_for, redirect
from kryptoexchange.forms import MovementForm
from datetime import datetime, date, time
import sqlite3
import requests

DBfile = app.config['DBFILE']
API_KEY = app.config['API_KEY']

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
    return render_template('listamovimientos.html', transacciones=transacciones, preciounitario=preciounitario) 

@app.route('/compra', methods=["GET", "POST"])
def nuevaCompra():
    form = MovementForm()
    if request.method == "POST":
        if form.validate():
            if 'calculadora' in request.form:
                print(request.form)
                if form.from_currency.data == form.to_currency.data:
                    flash('Las monedas son iguales.')
                    return render_template('compra.html', form=form)
                print('¡Hola!')
                url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(form.q1.data, form.from_currency.data, form.to_currency.data, API_KEY)
                respuesta = requests.get(url)
                ey = respuesta.json()
                diccionarioconprecio = (ey['data']['quote'][form.to_currency.data]['price'])
                q2 = float(diccionarioconprecio)
                preciounitario = float(form.q1.data/q2)
                return render_template("compra.html", form=form, cantidadconvertida=q2, preciounitario=preciounitario)
            else:
                if form.from_currency.data == form.to_currency.data :
                    flash('La operación debe realizarse con monedas o criptomonedas distintas')
                    return render_template('compra.html', form=form)
                print(request.form)
                now = datetime.now().time()
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
