from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, StringField
from wtforms.validators import DataRequired

class MovementForm(FlaskForm): #hereda de FlaskForm
    date = DateField('Fecha', validators=[DataRequired()])
    time = TimeField('Hora', validators=[DataRequired()])
    from_currency = StringField('De', validators=[DataRequired()])
