from kryptoexchange import app
from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, StringField, SubmitField, HiddenField, DecimalField, FloatField, SelectField, validators
from wtforms.validators import DataRequired, Length
import sqlite3


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


class MovementForm(FlaskForm): #hereda de FlaskForm
    from_currency = SelectField('From currency',
                            [validators.Required()],
                            choices=[])
    q1 = FloatField('Cantidad', validators=[DataRequired()])
    to_currency = SelectField('To currency',
                            [validators.Required()],
                            choices=listilla)
    q2 = FloatField('Importe a adquirir', validators=None)
    preciounitario = FloatField('Cantidad comprada', validators=None)
    calculadora = SubmitField('')
    submit = SubmitField('¡Compra ya!')

