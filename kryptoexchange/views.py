from kryptoexchange import app
from flask import render_template, flash, request, url_for, redirect
from kryptoexchange.forms import MovementForm
from datetime import datetime, date, time
import sqlite3
import requests
from sigfig import round
from decimal import Decimal

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
        precio_u = (transaccion['from_quantity'])/(transaccion['to_quantity'])
        preciounitario = Decimal(precio_u)
        if preciounitario >= 10:
            pru=float('{0:.2f}'.format(preciounitario))
        else:
            pru=round(preciounitario, sigfigs=4, type=Decimal)
        transaccion['preciounitario'] = pru
    return render_template('listamovimientos.html', transacciones=transacciones) 

@app.route('/compra', methods=["GET", "POST"])
def nuevaCompra():
    form = MovementForm()
    stock = consulta('SELECT to_currency, to_quantity FROM movements;')
    mismonedas=['EUR'] #TODO: Control de importes.
    for linea in stock:
        moneda = linea['to_currency']
        if moneda not in mismonedas:
            mismonedas.append(moneda)
    form.from_currency.choices=mismonedas
    if request.method == "POST":
        if 'calculadora' in request.form:
            if form.from_currency.data == form.to_currency.data:
                flash('Las monedas son iguales.')
                return render_template('compra.html', form=form)
            if form.from_currency.data != 'BTC' and form.to_currency.data == 'EUR':
                flash('Solo puedes convertir a EUR desde BTC')
                return render_template('compra.html', form=form)
            url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(form.q1.data, form.from_currency.data, form.to_currency.data, API_KEY)
            respuesta = requests.get(url)
            ey = respuesta.json()
            precio = (ey['data']['quote'][form.to_currency.data]['price'])
            preciounitario = round(form.q1.data/precio, sigfigs=4)
            form.q2.data=round(float(precio), sigfigs=4)
            return render_template("compra.html", form=form, cantidadconvertida=precio, preciounitario=preciounitario)
        else:
            if form.validate():
                if form.from_currency.data == form.to_currency.data :
                    flash('La operación debe realizarse con monedas o criptomonedas distintas')
                    return render_template('compra.html', form=form)
                today = date.today()
                fecha = today.strftime("%d/%m/%Y")
                hour = datetime.now().time()
                consulta('INSERT INTO movements (date, time, from_currency, from_quantity, to_currency, to_quantity) VALUES (?, ?, ?, ?, ?, ?);', 
                        (
                        str(fecha),
                        str(hour),
                        form.from_currency.data,
                        form.q1.data,
                        form.to_currency.data,
                        round(form.q2.data, sigfigs=4),
                        )
                    ) 
                return redirect(url_for('listaMovimientos')) #te devuelve a la página principal   
            else:
                return render_template("compra.html", form=form)
    return render_template("compra.html", form=form)


@app.route('/balance')
def balance():
    euros_invertidos = consulta('SELECT from_quantity FROM movements WHERE from_currency = "EUR"')
    inversion=0
    for euros in euros_invertidos:
        inversion+=(euros['from_quantity'])
    divisasdistintas = consulta('SELECT to_quantity, to_currency FROM movements WHERE to_currency <> "EUR"')
    print(divisasdistintas)
    valoractual=0
    for divisa in divisasdistintas: #TODO: Ver como arreglar esto. Lista previa. Demasiadas peticiones api, va lento. 
        url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(divisa['to_quantity'], divisa['to_currency'], 'EUR', API_KEY)
        respuesta = requests.get(url)
        ey = respuesta.json()
        precio = (ey['data']['quote']['EUR']['price'])
        valoractual += precio
    print(valoractual)
    balance=valoractual-inversion
    return render_template('balance.html', inversion=inversion, valoractual=valoractual, balance=balance)
