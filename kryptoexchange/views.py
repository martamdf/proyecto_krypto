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

def micarteracripto(): #Devuelve diccionario con las criptomonedas y su saldo correspondiente disponible.
    try:
        carteraactual={}
        transacciones = consulta('SELECT from_currency, from_quantity, to_currency, to_quantity FROM movements;')
        for transaccion in transacciones:
            if transaccion['to_currency'] not in carteraactual:
                carteraactual[transaccion['to_currency']] = transaccion['to_quantity']
            else: 
                carteraactual[transaccion['to_currency']] += transaccion['to_quantity']
            if transaccion['from_currency'] not in carteraactual:
                carteraactual[transaccion['from_currency']] = (0-transaccion['from_quantity'])
            else: 
                carteraactual[transaccion['from_currency']] -= transaccion['from_quantity']
        return carteraactual
    except:
        flash('Error al acceder a la base de datos')
        return render_template('compra.html')

def listamonedas():
    try:
        DBfile = app.config['DBFILE']
        conn = sqlite3.connect(DBfile)
        c = conn.cursor()
        c.execute('SELECT id FROM cryptos;')
        conn.commit()
        lista = c.fetchall()
        market_coins= []
        for moneda in lista:
            market_coins.append(moneda[0])
        conn.close()
        return market_coins
    except:
        market_coins=['EUR']

def controldeerrores_calculadora(form):
    if form.q1.data == None or isinstance (form.q1.data, str) or form.q1.data <= 0 :
        error = ('Formato numérico introducido no válido')
        return error
    if form.from_currency.data == form.to_currency.data:
        error = ('Error: Las monedas no pueden ser iguales.')
        return error
    if form.from_currency.data == 'EUR' and form.to_currency.data != 'BTC':
        error = ('Solo puedes utilizar BTCs para comprar esta moneda')
        return error
    if form.from_currency.data != 'BTC' and form.to_currency.data == 'EUR':
        error = ('Solo puedes convertir a EUR desde BTC')
        return error
    if form.q1.data > 1000000000:
        error = ('El importe máximo de conversión es de 1000000000')
        return error
    else:
        pass

def consulta_api(form):
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(form.q1.data, form.from_currency.data, form.to_currency.data, API_KEY)
    respuesta = requests.get(url)
    if respuesta.status_code ==200:
        resp_json = respuesta.json()
        return resp_json
    else:
        error = ('Se ha producido un error. APIKEY incorrecta')
        return error

@app.route('/')
def listaMovimientos():
    try:
        transacciones = consulta('SELECT id , date, time, from_currency, from_quantity, to_currency, to_quantity FROM movements;')
        for transaccion in transacciones:
            precio_u = (transaccion['from_quantity'])/(transaccion['to_quantity'])
            transaccion['preciounitario'] = redondea_valor(precio_u)
        return render_template('listamovimientos.html', transacciones=transacciones) 
    except:
        transacciones = []
        flash("Error en el acceso a la base de datos. No pueden mostrarse los movimientos")
        return render_template('listamovimientos.html', transacciones=transacciones) 

@app.route('/compra', methods=["GET", "POST"])
def nuevaCompra():
    form = MovementForm()
    try: #Acceso a la base de datos para crear la lista de monedas disponibles.
        micartera = micarteracripto()
        market_coins = listamonedas()
    except:
        flash('Error al acceso de la base de datos. Inténtelo de nuevo más tarde')
        return render_template('compra.html', form=form)
    mismonedas = list(micartera.keys())
    if 'EUR' not in mismonedas: 
        mismonedas.append('EUR')
    form.from_currency.choices=mismonedas
    form.to_currency.choices= market_coins

    if request.method == "POST":
        if 'calculadora' in request.form:
            error = controldeerrores_calculadora(form)
            if error:
                flash(error)
                return render_template('compra.html', form=form)
            resp_json = consulta_api(form)
            if not isinstance(resp_json, str):
                precio = (resp_json['data']['quote'][form.to_currency.data]['price'])
                cantidadconvertida = redondea_valor(precio)
                form.q2.data = cantidadconvertida
                preciounitario = redondea_valor(form.q1.data/precio)
                # generamos campos ocultos de la consulta
                form.to_currency_hidden.data = form.to_currency.data
                form.from_currency_hidden.data = form.from_currency.data
                form.q2_hidden.data = cantidadconvertida
                form.q1_hidden.data = form.q1.data
                return render_template("compra.html", form=form, cantidadconvertida=cantidadconvertida, preciounitario=preciounitario)
            else:
                error=('Se ha producido un error. APIKEY incorrecta')
                flash(error)
                return render_template('compra.html', form=form)
        else:
            if form.validate():
                carteraactual = micarteracripto()
                if form.from_currency_hidden.data != 'EUR':
                    disponible=float((carteraactual[form.from_currency_hidden.data]))
                if form.from_currency_hidden.data !='EUR' and float(form.q1_hidden.data) > disponible:
                    flash('No tienes suficiente saldo para realizar la operación.')
                    return render_template('compra.html', form=form)
                today = date.today()
                fecha = today.strftime("%d/%m/%Y")
                hora = datetime.now().time()
                try:
                    consulta('INSERT INTO movements (date, time, from_currency, from_quantity, to_currency, to_quantity) VALUES (?, ?, ?, ?, ?, ?);', 
                            (
                            str(fecha),
                            str(hora),
                            form.from_currency_hidden.data,
                            form.q1_hidden.data,
                            form.to_currency_hidden.data,
                            round(form.q2_hidden.data, sigfigs=4),
                            )
                        )
                    return redirect(url_for('listaMovimientos')) #te devuelve a la página principal
                except:
                    flash('Error al guardar. La operación no se ha realizado')
                    return render_template('compra.html', form=form)
            else:
                flash('Completa todos los datos del formulario antes de comprar.')
                return render_template("compra.html", form=form)
    return render_template("compra.html", form=form)

@app.route('/balance')
def balance():
    try:
        euros_from = consulta('SELECT from_quantity FROM movements WHERE from_currency = "EUR"')
        euros_to = consulta('SELECT to_quantity FROM movements WHERE to_currency = "EUR"')
    except:
        flash('Imposible acceder a la base de datos.')
        inversion=0
        return render_template('balance.html', inversion=inversion)
    saldo_euros_invertidos=0
    total_euros_invertidos=0
    for euros in euros_from:
        total_euros_invertidos += (euros['from_quantity'])
        saldo_euros_invertidos = saldo_euros_invertidos - (euros['from_quantity'])
    for euros in euros_to:
        saldo_euros_invertidos = saldo_euros_invertidos + (euros['to_quantity'])
    carteraactual = micarteracripto()
    if 'EUR' in carteraactual:
        carteraactual.pop('EUR')
    valoractual=0
    for clave, valor in carteraactual.items(): 
        if valor == 0:
            precio = 0
        else:
            url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(valor, clave, 'EUR', API_KEY)
            respuesta = requests.get(url)
            if respuesta.status_code ==200:
                dict_precios = respuesta.json()
                precio = (dict_precios['data']['quote']['EUR']['price'])
            else:
                flash('Error de API KEY. No podemos calcular tu balance')
                inversion = 0
                return render_template('balance.html', inversion=inversion)
        valoractual += precio
    misaldo= total_euros_invertidos + saldo_euros_invertidos + valoractual
    misaldo = redondea_valor(misaldo)
    balance = round((misaldo - total_euros_invertidos), decimals=3)
    return render_template('balance.html', inversion=total_euros_invertidos, valoractual=misaldo, balance=balance)


