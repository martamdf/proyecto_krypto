from kryptoexchange import app
from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, StringField, SubmitField, HiddenField, DecimalField, FloatField, SelectField, validators
from wtforms.validators import DataRequired, Length
import sqlite3


try:
    DBfile = app.config['DBFILE']
    conn = sqlite3.connect(DBfile)
    c = conn.cursor()
    c.execute('SELECT id FROM cryptos;')
    conn.commit()
    lista = c.fetchall()
    listilla= []
    for moneda in lista:
        listilla.append(moneda[0])
    conn.close()
except:
    listilla=['EUR']


class MovementForm(FlaskForm): #hereda de FlaskForm
    from_currency = SelectField('From currency',
                            [validators.Required()],
                            choices=[])
    from_currency_hidden=HiddenField('hidden')
    q1 = FloatField('Cantidad', validators=[DataRequired()])
    q1_hidden = HiddenField()
    to_currency = SelectField('To currency',
                            [validators.Required()],
                            choices=listilla)
    to_currency_hidden = HiddenField()
    q2 = FloatField('Importe a adquirir', validators=None)
    q2_hidden = HiddenField(validators=None)
    preciounitario = FloatField('Cantidad comprada', validators=None)
    preciounitario_hidden = HiddenField(validators=None)
    calculadora = SubmitField('')
    submit = SubmitField('¡Compra ya!')

