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

def redondea_valor(precio):
    precio_bruto = Decimal(precio)
    if precio_bruto >= 10:
        precio_redondeado=float('{0:.2f}'.format(precio_bruto))
    else:
        precio_redondeado=round(precio_bruto, sigfigs=4, type=Decimal)
    return precio_redondeado

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

def monedas_disponibles():
    stock = consulta('SELECT to_currency, to_quantity FROM movements;')
    mismonedas=['EUR']
    for linea in stock:
        moneda = linea['to_currency']
        if moneda not in mismonedas:
            mismonedas.append(moneda)
    return mismonedas

@app.route('/')
def listaMovimientos():
    transacciones = consulta('SELECT id , date, time, from_currency, from_quantity, to_currency, to_quantity FROM movements;')
    for transaccion in transacciones:
        print(transaccion)
        precio_u = (transaccion['from_quantity'])/(transaccion['to_quantity'])
        transaccion['preciounitario'] = redondea_valor(precio_u)
    return render_template('listamovimientos.html', transacciones=transacciones) 

@app.route('/compra', methods=["GET", "POST"])
def nuevaCompra():
    form = MovementForm()
    mismonedas = monedas_disponibles()
    form.from_currency.choices=mismonedas
    if request.method == "POST":
        if 'calculadora' in request.form:
            if form.q1.data == None or isinstance (form.q1.data, str) or form.q1.data <= 0 :
                flash('Formato numérico introducido no válido')
                return render_template('compra.html', form=form)
            if form.from_currency.data == form.to_currency.data:
                flash('Error: Las monedas no pueden ser iguales.')
                return render_template('compra.html', form=form)
            if form.from_currency.data == 'EUR' and form.to_currency.data != 'BTC':
                flash('Solo puedes utilizar BTCs para comprar esta moneda')
                return render_template('compra.html', form=form)
            if form.from_currency.data != 'BTC' and form.to_currency.data == 'EUR':
                flash('Solo puedes convertir a EUR desde BTC')
                return render_template('compra.html', form=form)
            if form.q1.data > 1000000000:
                flash('El importe máximo de conversión es de 1000000000')
                return render_template('compra.html', form=form)
            url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(form.q1.data, form.from_currency.data, form.to_currency.data, API_KEY)
            respuesta = requests.get(url)
            if respuesta.status_code ==200:
                ey = respuesta.json()
                precio = (ey['data']['quote'][form.to_currency.data]['price'])
                cantidadconvertida = redondea_valor(precio)
                form.q2.data = cantidadconvertida
                form.q2_hidden.data = cantidadconvertida
                form.q1_hidden.data = form.q1.data
                form.to_currency_hidden.data = form.to_currency.data
                form.from_currency_hidden.data = form.from_currency.data
                preciounitario = redondea_valor(form.q1.data/precio)
                form.preciounitario_hidden.data = preciounitario
                return render_template("compra.html", form=form, cantidadconvertida=cantidadconvertida, preciounitario=preciounitario)
            else:
                flash('Se ha producido un error. APIKEY incorrecta')
                return render_template('compra.html', form=form)
        else:
            if form.validate():
                print(request.form)
                carteraactual={}
                divisasdistintas = consulta('SELECT to_quantity, to_currency FROM movements WHERE to_currency <> "EUR"')
                for cripto in divisasdistintas:
                    if cripto['to_currency'] not in carteraactual:
                        carteraactual[cripto['to_currency']]=cripto['to_quantity']
                    else:
                        carteraactual[cripto['to_currency']]=cripto['to_quantity']+(carteraactual[cripto['to_currency']])
                if form.from_currency_hidden.data != 'EUR':
                    disponible=float((carteraactual[form.from_currency_hidden.data]))
                if form.from_currency_hidden.data !='EUR' and float(form.q1_hidden.data) > disponible:
                    flash('No tienes suficiente saldo para realizar la operación.')
                    return render_template('compra.html', form=form)
                today = date.today()
                fecha = today.strftime("%d/%m/%Y")
                hour = datetime.now().time()
                consulta('INSERT INTO movements (date, time, from_currency, from_quantity, to_currency, to_quantity) VALUES (?, ?, ?, ?, ?, ?);', 
                        (
                        str(fecha),
                        str(hour),
                        form.from_currency_hidden.data,
                        form.q1_hidden.data,
                        form.to_currency_hidden.data,
                        round(form.q2_hidden.data, sigfigs=4),
                        )
                    ) 
                return redirect(url_for('listaMovimientos')) #te devuelve a la página principal   
            else:
                flash('Completa todos los datos del formulario antes de comprar.')
                return render_template("compra.html", form=form)
    return render_template("compra.html", form=form)

@app.route('/balance')
def balance():
    euros_from = consulta('SELECT from_quantity FROM movements WHERE from_currency = "EUR"')
    euros_to = consulta('SELECT to_quantity FROM movements WHERE to_currency = "EUR"')
    saldo_euros_invertidos=0
    total_euros_invertidos=0
    carteraactual={}
    for euros in euros_from:
        total_euros_invertidos += (euros['from_quantity'])
        saldo_euros_invertidos = saldo_euros_invertidos - (euros['from_quantity'])
    for euros in euros_to:
        saldo_euros_invertidos = saldo_euros_invertidos + (euros['to_quantity'])
    transacciones = consulta('SELECT from_currency, from_quantity, to_currency, to_quantity FROM movements;')
    for transaccion in transacciones:
        print(transaccion)
        if transaccion['to_currency'] not in carteraactual:
            carteraactual[transaccion['to_currency']]=transaccion['to_quantity']
            if transaccion['from_currency'] in carteraactual:
                carteraactual[transaccion['from_currency']]= (carteraactual[transaccion['from_currency']]) - transaccion['from_quantity']
        else:
            carteraactual[transaccion['to_currency']]=transaccion['to_quantity']+(carteraactual[transaccion['to_currency']])
            if transaccion['from_currency'] in carteraactual:
                carteraactual[transaccion['from_currency']]= (carteraactual[transaccion['from_currency']]) - transaccion['from_quantity']

    valoractual=0
    for clave, valor in carteraactual.items(): #TODO: OJO EXCEPCIONES API
        if valor == 0:
            precio = 0
        else:
            url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(valor, clave, 'EUR', API_KEY)
            respuesta = requests.get(url)
            ey = respuesta.json()
            precio = (ey['data']['quote']['EUR']['price'])
        valoractual += precio
    misaldo=round(valoractual, decimals=2)
    misaldo= total_euros_invertidos + saldo_euros_invertidos + valoractual
    balance = round((misaldo - total_euros_invertidos), decimals=3)
    return render_template('balance.html', inversion=total_euros_invertidos, valoractual=misaldo, balance=balance)
